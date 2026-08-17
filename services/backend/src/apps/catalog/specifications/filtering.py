from typing import (
    List,
    Tuple,
    Any,
    Optional,
    Union,
    Set
)

from apps.catalog.interfaces.specifications import FilterSpecificationInterface
from apps.catalog.specifications.clauses import EFFECTIVE_PRICE, INVENTORY_ALIAS, PRODUCT_ALIAS, SqlClause


class ProductFilterSpecification(FilterSpecificationInterface):
    """Specification for filtering products"""

    def __init__(self):
        self._min_year: Optional[int] = None
        self._max_year: Optional[int] = None
        self._min_price: Optional[float] = None
        self._max_price: Optional[float] = None
        self._genders: Optional[Set[str]] = None
        self._is_available: Optional[bool] = None

    def set_year_range(self, min_year: Optional[int] = None, max_year: Optional[int] = None) -> None:
        """
        Set year range filter

        Args:
            min_year: Minimum year (inclusive)
            max_year: Maximum year (inclusive)
        """
        self._min_year = min_year
        self._max_year = max_year

    def set_price_range(self, min_price: Optional[float] = None, max_price: Optional[float] = None) -> None:
        """
        Set price range filter

        Args:
            min_price: Minimum price (inclusive)
            max_price: Maximum price (inclusive)
        """
        self._min_price = min_price
        self._max_price = max_price

    def set_genders(self, genders: Union[str, List[str]]) -> None:
        """
        Set gender filter

        Args:
            genders: Gender or list of genders to filter by.
                    Input is case-insensitive and will be converted to proper case.
        """
        if isinstance(genders, str):
            genders = [g.strip() for g in genders.split(',')]

        self._genders = {self._capitalize_gender(gender) for gender in genders if gender}

    def set_availability(self, is_available: bool) -> None:
        """
        Set availability filter

        Args:
            is_available: True to show only available products, False to show only unavailable
        """
        self._is_available = is_available

    @staticmethod
    def _capitalize_gender(gender: str) -> str:
        """
        Convert gender value to correct case for database

        Args:
            gender: Gender value in any case

        Returns:
            Gender value with first letter capitalized
        """
        return gender.strip().capitalize() if gender else ''

    def is_empty(self) -> bool:
        """
        Check if filter specification has any filters

        Returns:
            True if no filters are defined, False otherwise
        """
        return (
                self._min_year is None and
                self._max_year is None and
                self._min_price is None and
                self._max_price is None and
                (self._genders is None or len(self._genders) == 0) and
                self._is_available is None
        )

    def to_clause(self) -> SqlClause:
        """
        Build the predicates this filter contributes

        Every column is already qualified with the alias the repository uses, so
        nothing downstream has to rewrite the text to make it valid.

        Returns:
            Conditions with the values they bind
        """
        conditions = []
        params = []

        if self._min_year is not None:
            conditions.append(f"{PRODUCT_ALIAS}.year >= %s")
            params.append(self._min_year)

        if self._max_year is not None:
            conditions.append(f"{PRODUCT_ALIAS}.year <= %s")
            params.append(self._max_year)

        if self._min_price is not None:
            conditions.append(f"{EFFECTIVE_PRICE} >= %s")
            params.append(self._min_price)

        if self._max_price is not None:
            conditions.append(f"{EFFECTIVE_PRICE} <= %s")
            params.append(self._max_price)

        if self._genders:
            placeholders = ", ".join(["%s"] * len(self._genders))
            conditions.append(f"{PRODUCT_ALIAS}.gender IN ({placeholders})")
            params.extend(self._genders)

        if self._is_available is not None:
            conditions.append(self._availability_condition())

        return SqlClause(conditions=conditions, params=params)

    def _availability_condition(self) -> str:
        """
        Build the condition describing what "available" means

        Availability is both flags at once: a deactivated product is unavailable
        however much stock sits on the shelf.

        Returns:
            Condition matching available or unavailable products
        """
        if self._is_available:
            return f"({INVENTORY_ALIAS}.is_active AND {INVENTORY_ALIAS}.is_in_stock)"

        return (
            f"(NOT {INVENTORY_ALIAS}.is_active OR NOT {INVENTORY_ALIAS}.is_in_stock "
            f"OR {INVENTORY_ALIAS}.id IS NULL)"
        )

    def add_filter(self, field: str, value: Any) -> None:
        """
        Add a filter criterion

        Args:
            field: Field name to filter on
            value: Value to filter by
        """
        if field == 'min_year' and value is not None:
            self._min_year = int(value)
        elif field == 'max_year' and value is not None:
            self._max_year = int(value)
        elif field == 'min_price' and value is not None:
            self._min_price = float(value)
        elif field == 'max_price' and value is not None:
            self._max_price = float(value)
        elif field == 'gender' and value:
            self.set_genders(value)
        elif field == 'is_available' and value is not None:
            self.set_availability(bool(value))
