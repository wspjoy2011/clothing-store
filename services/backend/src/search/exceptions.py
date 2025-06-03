"""Custom exceptions for Elasticsearch search operations."""


class SearchException(Exception):
    """Base exception for all search-related errors."""

    def __init__(self, message: str, original_error: Exception = None):
        super().__init__(message)
        self.original_error = original_error


class ElasticsearchConnectionError(SearchException):
    """Raised when connection to Elasticsearch fails."""
    pass


class ElasticsearchQueryError(SearchException):
    """Raised when Elasticsearch query execution fails."""
    pass


class ElasticsearchIndexError(SearchException):
    """Raised when there's an issue with Elasticsearch index."""
    pass


class AutocompleteError(SearchException):
    """Raised when autocomplete operation fails."""
    pass
