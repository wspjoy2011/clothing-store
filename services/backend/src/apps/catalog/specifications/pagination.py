from typing import Any

from apps.catalog.interfaces.specifications import PaginationSpecificationInterface


class PaginationSpecification(PaginationSpecificationInterface):
    """Specification for pagination"""

    def __init__(self, page: int, per_page: int):
        self._offset = (page - 1) * per_page
        self._limit = per_page

    def to_sql(self) -> tuple[str, list[Any]]:
        """Convert to SQL OFFSET/LIMIT clause"""
        return "OFFSET %s LIMIT %s", [self._offset, self._limit]

    def get_offset(self) -> int:
        return self._offset

    def get_limit(self) -> int:
        return self._limit
