"""Custom exceptions and error handling."""
from typing import Any, Dict, Optional


class TaskManagementException(Exception):
    """Base exception for Task Management System."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(TaskManagementException):
    """Authentication related errors."""

    def __init__(
        self,
        message: str = "Authentication failed",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message=message, status_code=401, details=details)


class AuthorizationError(TaskManagementException):
    """Authorization related errors."""

    def __init__(
        self,
        message: str = "Permission denied",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message=message, status_code=403, details=details)


class NotFoundError(TaskManagementException):
    """Resource not found errors."""

    def __init__(
        self,
        message: str = "Resource not found",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message=message, status_code=404, details=details)


class ValidationError(TaskManagementException):
    """Validation errors."""

    def __init__(
        self,
        message: str = "Validation failed",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message=message, status_code=422, details=details)


class ConflictError(TaskManagementException):
    """Conflict errors (e.g., duplicate entries)."""

    def __init__(
        self,
        message: str = "Resource conflict",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message=message, status_code=409, details=details)


class FileUploadError(TaskManagementException):
    """File upload related errors."""

    def __init__(
        self,
        message: str = "File upload failed",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message=message, status_code=400, details=details)
