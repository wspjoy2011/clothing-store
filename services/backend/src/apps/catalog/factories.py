from typing import Optional

from apps.catalog.interfaces.specifications import (
    PaginationSpecificationInterface,
    OrderingSpecificationInterface,
    FilterSpecificationInterface,
    SearchSpecificationInterface, CategorySpecificationInterface
)
from apps.catalog.specifications.filtering import ProductFilterSpecification
from apps.catalog.specifications.pagination import PaginationSpecification
from apps.catalog.specifications.ordering import OrderingSpecification
from apps.catalog.specifications.search import ProductSearchSpecification


def create_pagination_specification(page: int, per_page: int) -> PaginationSpecificationInterface:
    """Factory function to create pagination specification"""
    return PaginationSpecification(page, per_page)


def create_ordering_specification(ordering: Optional[str] = None) -> OrderingSpecificationInterface:
    """Factory function to create ordering specification"""
    return OrderingSpecification(ordering)


def create_product_filter_specification(
        min_year: Optional[int] = None,
        max_year: Optional[int] = None,
        gender: Optional[str] = None
) -> FilterSpecificationInterface:
    """
    Create a product filter specification

    Args:
        min_year: Minimum year (inclusive)
        max_year: Maximum year (inclusive)
        gender: Gender(s) to filter by (comma-separated list)

    Returns:
        Initialized filter specification
    """
    spec = ProductFilterSpecification()

    if min_year is not None or max_year is not None:
        spec.set_year_range(min_year, max_year)

    if gender:
        spec.set_genders(gender)

    return spec


def create_search_specification(query: Optional[str] = None) -> SearchSpecificationInterface:
    """
    Create a search specification

    Args:
        query: Search query string

    Returns:
        SearchSpecificationInterface implementation
    """
    return ProductSearchSpecification(query)


def create_category_specification(
        master_category_id: int,
        sub_category_id: Optional[int] = None,
        article_type_id: Optional[int] = None
) -> CategorySpecificationInterface:
    """
    Create a category specification for filtering products by category hierarchy

    Args:
        master_category_id: Master category ID
        sub_category_id: Optional subcategory ID
        article_type_id: Optional article type ID

    Returns:
        Initialized category specification
    """
    from apps.catalog.specifications.category import CategorySpecification

    return CategorySpecification(
        master_category_id=master_category_id,
        sub_category_id=sub_category_id,
        article_type_id=article_type_id
    )
