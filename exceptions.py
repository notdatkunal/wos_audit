"""
Application-level exceptions for consistent error handling.
Repositories and services raise these; the API layer maps them to HTTP responses.
"""


class DatabaseError(Exception):
    """Raised when a database operation fails (connection, query, constraint, etc.)."""
    def __init__(self, message: str, cause: Exception | None = None):
        self.message = message
        self.cause = cause
        super().__init__(message)


class NotFoundError(Exception):
    """Raised when a requested resource is not found."""
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message)
