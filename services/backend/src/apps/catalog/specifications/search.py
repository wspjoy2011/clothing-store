from typing import Optional, Tuple, List, Any

from apps.catalog.interfaces.specifications import SearchSpecificationInterface


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

    def to_sql(self) -> Tuple[str, List[Any]]:
        """
        Convert search specification to SQL WHERE clause and params

        Returns:
            Tuple of (SQL WHERE clause, parameters list)
        """
        if self.is_empty():
            return "", []

        sql = """
        WHERE to_tsvector('public.english_unaccent', product_display_name) @@ plainto_tsquery('public.english_unaccent', %s)
        ORDER BY ts_rank(to_tsvector('public.english_unaccent', product_display_name), 
                        plainto_tsquery('public.english_unaccent', %s)) DESC
        """
        return sql, [self._query, self._query]
