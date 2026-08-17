from typing import Optional, Tuple, List, Any

from apps.catalog.interfaces.specifications import SearchSpecificationInterface
from apps.catalog.specifications.clauses import PRODUCT_ALIAS, SqlClause

SEARCH_CONFIGURATION = "public.english_unaccent"


class ProductSearchSpecification(SearchSpecificationInterface):
    """Specification for product text search with relevance ranking."""

    def __init__(self, query: Optional[str] = None):
        """
        Initialize search specification

        Args:
            query: Search query text
        """
        self._query = query.strip() if query else None

    @property
    def query(self) -> Optional[str]:
        """Get the search query."""
        return self._query

    def is_empty(self) -> bool:
        """Check if the search specification is empty."""
        return self._query is None or self._query == ""

    def to_clause(self) -> SqlClause:
        """
        Build the full-text predicate for the query

        Returns:
            Condition matching the searched products, with its parameter
        """
        if self.is_empty():
            return SqlClause()

        return SqlClause(
            conditions=[
                f"to_tsvector('{SEARCH_CONFIGURATION}', {PRODUCT_ALIAS}.product_display_name) "
                f"@@ plainto_tsquery('{SEARCH_CONFIGURATION}', %s)"
            ],
            params=[self._query]
        )

    def relevance_order(self) -> Tuple[str, List[Any]]:
        """
        Build the ordering expression ranking matches by relevance

        Returns:
            Expression and the parameter it binds, empty when nothing is searched
        """
        if self.is_empty():
            return "", []

        expression = (
            f"ts_rank(to_tsvector('{SEARCH_CONFIGURATION}', {PRODUCT_ALIAS}.product_display_name), "
            f"plainto_tsquery('{SEARCH_CONFIGURATION}', %s)) DESC"
        )
        return expression, [self._query]
