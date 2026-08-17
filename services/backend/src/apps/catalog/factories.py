from typing import Optional

from apps.catalog.interfaces.factories import SpecificationFactoryInterface
from apps.catalog.interfaces.specifications import (
    CategorySpecificationInterface,
    FilterSpecificationInterface,
    OrderingSpecificationInterface,
    PaginationSpecificationInterface,
    SearchSpecificationInterface,
)
from apps.catalog.specifications.filtering import ProductFilterSpecification
from apps.catalog.specifications.ordering import OrderingSpecification
from apps.catalog.specifications.pagination import PaginationSpecification
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
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        gender: Optional[str] = None,
        is_available: Optional[bool] = None
) -> FilterSpecificationInterface:
    """
    Create a product filter specification

    Args:
        min_year: Minimum year (inclusive)
        max_year: Maximum year (inclusive)
        min_price: Minimum price (inclusive)
        max_price: Maximum price (inclusive)
        gender: Gender(s) to filter by (comma-separated list)
        is_available: True to show only available products, False to show only unavailable

    Returns:
        Initialized filter specification
    """
    spec = ProductFilterSpecification()

    if min_year is not None or max_year is not None:
        spec.set_year_range(min_year, max_year)

    if min_price is not None or max_price is not None:
        spec.set_price_range(min_price, max_price)

    if gender:
        spec.set_genders(gender)

    if is_available is not None:
        spec.set_availability(is_available)

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


class SpecificationFactory(SpecificationFactoryInterface):
    """Builds catalogue specifications from the values a request carries"""

    def pagination(self, page: int, per_page: int) -> PaginationSpecificationInterface:
        """Build the pagination of one page"""
        return create_pagination_specification(page, per_page)

    def ordering(self, ordering: Optional[str] = None) -> OrderingSpecificationInterface:
        """Build the ordering the client asked for"""
        return create_ordering_specification(ordering)

    def filters(
            self,
            min_year: Optional[int] = None,
            max_year: Optional[int] = None,
            min_price: Optional[float] = None,
            max_price: Optional[float] = None,
            gender: Optional[str] = None,
            is_available: Optional[bool] = None
    ) -> FilterSpecificationInterface:
        """Build the filter over product and inventory attributes"""
        return create_product_filter_specification(
            min_year, max_year, min_price, max_price, gender, is_available
        )

    def search(self, query: Optional[str] = None) -> SearchSpecificationInterface:
        """Build the full-text search of a query"""
        return create_search_specification(query)

    def category(
            self,
            master_category_id: int,
            sub_category_id: Optional[int] = None,
            article_type_id: Optional[int] = None
    ) -> CategorySpecificationInterface:
        """Build the selection of one branch of the category tree"""
        return create_category_specification(master_category_id, sub_category_id, article_type_id)
