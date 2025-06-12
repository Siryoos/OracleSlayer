"""Custom exceptions for oradb-extractor."""


class ExtractionError(Exception):
    """Base class for extraction errors."""


class ConnectionError(ExtractionError):
    """Raised when a connection cannot be established."""


class QueryError(ExtractionError):
    """Raised when a query fails."""
