from typing import Any, Optional

from apps.catalog.interfaces.specifications import OrderingSpecificationInterface


class OrderingSpecification(OrderingSpecificationInterface):
    """Specification for ordering results"""

    FIELD_EXPRESSIONS = {
        "id": "id",
        "year": "year",
        "product_id": "product_id",
        "price": "COALESCE(i.sale_price, i.base_price)"
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

    def to_sql(self) -> tuple[str, list[Any]]:
        """
        Build the ORDER BY clause from allowlisted expressions only

        Returns:
            The clause and an empty parameter list
        """
        sql_parts = []

        for field in self._ordering_fields:
            expression = self.FIELD_EXPRESSIONS[self._field_name_of(field)]
            direction = "DESC" if field.startswith('-') else "ASC"
            sql_parts.append(f"{expression} {direction}")

        sql = f"ORDER BY {', '.join(sql_parts)}"
        return sql, []

    def get_ordering_fields(self) -> list[str]:
        """Get the list of ordering fields"""
        return self._ordering_fields.copy()
