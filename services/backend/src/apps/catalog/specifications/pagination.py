
from apps.catalog.interfaces.specifications import PaginationSpecificationInterface


class PaginationSpecification(PaginationSpecificationInterface):
    """Specification for pagination"""

    def __init__(self, page: int, per_page: int):
        self._offset = (page - 1) * per_page
        self._limit = per_page

    def get_offset(self) -> int:
        return self._offset

    def get_limit(self) -> int:
        return self._limit
