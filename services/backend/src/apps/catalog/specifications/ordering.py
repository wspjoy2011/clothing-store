from typing import Any, Optional

from apps.catalog.interfaces.specifications import OrderingSpecificationInterface
from apps.catalog.specifications.clauses import EFFECTIVE_PRICE, PRODUCT_ALIAS


class OrderingSpecification(OrderingSpecificationInterface):
    """Specification for ordering results"""

    FIELD_EXPRESSIONS = {
        "id": f"{PRODUCT_ALIAS}.product_id",
        "year": f"{PRODUCT_ALIAS}.year",
        "product_id": f"{PRODUCT_ALIAS}.product_id",
        "price": EFFECTIVE_PRICE
    }

    DEFAULT_ORDERING = "-id"
    TIEBREAKER = "product_id"

    def __init__(self, ordering: Optional[str] = None):
        self._allowed_fields = list(self.FIELD_EXPRESSIONS)

        self._ordering_fields = self._parse_ordering(ordering)

    def _parse_ordering(self, ordering_param: Optional[str]) -> list[str]:
        """
        Keep the requested fields that are on the allowlist, in the order asked for

        A field is recognised only as an exact allowlisted name with at most one
        leading minus. Anything else is dropped: stripping every leading minus
        would let "---id" pass as "id" and reach the SQL as "--id", where the two
        dashes comment out the rest of the statement.

        Args:
            ordering_param: Comma-separated fields as received from the client

        Returns:
            Recognised fields, always ending with the tiebreaker
        """
        if not ordering_param:
            return [self.DEFAULT_ORDERING]

        processed_fields = [
            field for field in ordering_param.split(',')
            if self._field_name_of(field) in self.FIELD_EXPRESSIONS
        ]

        if not processed_fields:
            return [self.DEFAULT_ORDERING]

        if not any(self._field_name_of(field) == self.TIEBREAKER for field in processed_fields):
            processed_fields.append(self.TIEBREAKER)

        return processed_fields

    @staticmethod
    def _field_name_of(field: str) -> str:
        """
        Read the field name of a possibly descending field

        Args:
            field: Field as written by the client, optionally prefixed with one minus

        Returns:
            The name without its direction prefix
        """
        return field[1:] if field.startswith('-') else field

    def to_order_by(self) -> list[str]:
        """
        Build the ordering expressions from allowlisted columns only

        Returns:
            Expressions in the order they apply
        """
        return [
            f"{self.FIELD_EXPRESSIONS[self._field_name_of(field)]} "
            f"{'DESC' if field.startswith('-') else 'ASC'}"
            for field in self._ordering_fields
        ]

    @property
    def is_default(self) -> bool:
        """Report whether the client asked for no particular order"""
        return self._ordering_fields == [self.DEFAULT_ORDERING]

    def is_empty(self) -> bool:
        """Ordering always contributes an order, if only the default one"""
        return False

    def get_ordering_fields(self) -> list[str]:
        """Get the list of ordering fields"""
        return self._ordering_fields.copy()
