from typing import Optional

from apps.catalog.interfaces.specifications import (
    PaginationSpecificationInterface,
    OrderingSpecificationInterface
)
from apps.catalog.specifications.pagination import PaginationSpecification
from apps.catalog.specifications.ordering import OrderingSpecification


def create_pagination_specification(page: int, per_page: int) -> PaginationSpecificationInterface:
    """Factory function to create pagination specification"""
    return PaginationSpecification(page, per_page)


def create_ordering_specification(ordering: Optional[str] = None) -> OrderingSpecificationInterface:
    """Factory function to create ordering specification"""
    return OrderingSpecification(ordering)
