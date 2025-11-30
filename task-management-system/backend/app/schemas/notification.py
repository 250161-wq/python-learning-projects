"""Notification-related Pydantic schemas."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.notification import NotificationType


class NotificationCreate(BaseModel):
    """Schema for creating a notification."""

    user_id: int
    type: NotificationType
    title: str
    message: str
    related_task_id: Optional[int] = None
    related_team_id: Optional[int] = None


class NotificationResponse(BaseModel):
    """Schema for notification response."""

    id: int
    user_id: int
    type: NotificationType
    title: str
    message: str
    related_task_id: Optional[int]
    related_team_id: Optional[int]
    is_read: bool
    created_at: datetime
    read_at: Optional[datetime]

    class Config:
        from_attributes = True
