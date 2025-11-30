"""Common schemas used across the application."""
from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper."""

    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    """Simple message response."""

    message: str
    success: bool = True
    details: Optional[dict] = None
