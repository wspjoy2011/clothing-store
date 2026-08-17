from abc import ABC, abstractmethod
from typing import Optional

from apps.catalog.interfaces.specifications import (
    CategorySpecificationInterface,
    FilterSpecificationInterface,
    OrderingSpecificationInterface,
    PaginationSpecificationInterface,
    SearchSpecificationInterface,
)


class SpecificationFactoryInterface(ABC):
    """Builds the specifications a catalogue query is assembled from

    One collaborator rather than five: they are always injected together, and a
    service taking each of them separately makes every test assemble a graph of
    stand-ins to exercise a single method.
    """

    @abstractmethod
    def pagination(self, page: int, per_page: int) -> PaginationSpecificationInterface:
        """
        Build the pagination of one page

        Args:
            page: Page number, starting at one
            per_page: Items per page

        Returns:
            Pagination specification
        """
        pass

    @abstractmethod
    def ordering(self, ordering: Optional[str] = None) -> OrderingSpecificationInterface:
        """
        Build the ordering the client asked for

        Args:
            ordering: Comma-separated fields, optionally prefixed with a minus

        Returns:
            Ordering specification
        """
        pass

    @abstractmethod
    def filters(
            self,
            min_year: Optional[int] = None,
            max_year: Optional[int] = None,
            min_price: Optional[float] = None,
            max_price: Optional[float] = None,
            gender: Optional[str] = None,
            is_available: Optional[bool] = None
    ) -> FilterSpecificationInterface:
        """
        Build the filter over product and inventory attributes

        Args:
            min_year: Minimum year, inclusive
            max_year: Maximum year, inclusive
            min_price: Minimum effective price, inclusive
            max_price: Maximum effective price, inclusive
            gender: Comma-separated gender values
            is_available: Availability to select

        Returns:
            Filter specification
        """
        pass

    @abstractmethod
    def search(self, query: Optional[str] = None) -> SearchSpecificationInterface:
        """
        Build the full-text search of a query

        Args:
            query: Text to search for

        Returns:
            Search specification
        """
        pass

    @abstractmethod
    def category(
            self,
            master_category_id: int,
            sub_category_id: Optional[int] = None,
            article_type_id: Optional[int] = None
    ) -> CategorySpecificationInterface:
        """
        Build the selection of one branch of the category tree

        Args:
            master_category_id: Master category to select
            sub_category_id: Optional sub-category to narrow to
            article_type_id: Optional article type to narrow to

        Returns:
            Category specification
        """
        pass
