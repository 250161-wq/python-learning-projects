"""Attachment-related Pydantic schemas."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AttachmentCreate(BaseModel):
    """Schema for creating an attachment."""

    task_id: int
    filename: str
    original_filename: str
    file_path: str
    file_size: int
    content_type: str


class AttachmentResponse(BaseModel):
    """Schema for attachment response."""

    id: int
    task_id: int
    uploaded_by_id: int
    filename: str
    original_filename: str
    file_size: int
    content_type: str
    created_at: datetime
    download_url: Optional[str] = None

    class Config:
        from_attributes = True
