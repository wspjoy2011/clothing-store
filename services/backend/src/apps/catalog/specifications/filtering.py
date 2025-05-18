from typing import (
    List,
    Tuple,
    Any,
    Optional,
    Union,
    Set
)
from apps.catalog.interfaces.specifications import FilterSpecificationInterface


class ProductFilterSpecification(FilterSpecificationInterface):
    """Specification for filtering products"""

    def __init__(self):
        self._min_year: Optional[int] = None
        self._max_year: Optional[int] = None
        self._genders: Optional[Set[str]] = None

    def set_year_range(self, min_year: Optional[int] = None, max_year: Optional[int] = None) -> None:
        """
        Set year range filter

        Args:
            min_year: Minimum year (inclusive)
            max_year: Maximum year (inclusive)
        """
        self._min_year = min_year
        self._max_year = max_year

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
                (self._genders is None or len(self._genders) == 0)
        )

    def to_sql(self) -> Tuple[str, List[Any]]:
        """
        Convert filter specification to SQL WHERE clause with parameters

        Returns:
            Tuple containing SQL WHERE clause and list of parameters
        """
        conditions = []
        params = []

        if self._min_year is not None:
            conditions.append("year >= %s")
            params.append(self._min_year)

        if self._max_year is not None:
            conditions.append("year <= %s")
            params.append(self._max_year)

        if self._genders and len(self._genders) > 0:
            placeholders = ', '.join(['%s'] * len(self._genders))
            conditions.append(f"gender IN ({placeholders})")
            params.extend(self._genders)

        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)
            return where_clause, params

        return "", []

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
        elif field == 'gender' and value:
            self.set_genders(value)
