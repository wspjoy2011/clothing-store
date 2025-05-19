from typing import Any, Optional

from apps.catalog.interfaces.specifications import OrderingSpecificationInterface


class OrderingSpecification(OrderingSpecificationInterface):
    """Specification for ordering results"""

    def __init__(self, ordering: Optional[str] = None):
        self._allowed_fields = ["id", "year"]

        self._ordering_fields = self._parse_ordering(ordering)

    def _parse_ordering(self, ordering_param: Optional[str]) -> list[str]:
        """Parse and validate ordering parameter"""
        if not ordering_param:
            return ["-id"]

        ordering_fields = ordering_param.split(',')

        all_allowed_fields = set(self._allowed_fields + [f"-{field}" for field in self._allowed_fields])

        processed_fields = [field for field in ordering_fields if field.lstrip('-') in all_allowed_fields]

        if not processed_fields:
            return ["-id"]

        return processed_fields

    def to_sql(self) -> tuple[str, list[Any]]:
        """Convert ordering fields to SQL ORDER BY clause"""
        sql_parts = []

        for field in self._ordering_fields:
            if field.startswith('-'):
                sql_parts.append(f"{field[1:]} DESC")
            else:
                sql_parts.append(f"{field} ASC")

        sql = f"ORDER BY {', '.join(sql_parts)}"
        return sql, []

    def get_ordering_fields(self) -> list[str]:
        """Get the list of ordering fields"""
        return self._ordering_fields.copy()
