"""Custom exceptions for data synchronization operations."""


class SyncException(Exception):
    """Base exception for all synchronization-related errors."""

    def __init__(self, message: str, original_error: Exception = None):
        super().__init__(message)
        self.original_error = original_error


class DataExtractionError(SyncException):
    """Raised when data extraction from source fails."""
    pass


class DataLoadingError(SyncException):
    """Raised when data loading to destination fails."""
    pass


class MigrationError(SyncException):
    """Raised when data migration process fails."""
    pass


class IndexOperationError(SyncException):
    """Raised when index operations fail."""
    pass
