"""Notification model for real-time notifications."""
import enum
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, Text, DateTime, Enum, ForeignKey, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class NotificationType(str, enum.Enum):
    """Types of notifications."""

    TASK_ASSIGNED = "task_assigned"
    TASK_UPDATED = "task_updated"
    TASK_COMPLETED = "task_completed"
    TASK_DUE_SOON = "task_due_soon"
    TASK_OVERDUE = "task_overdue"
    TEAM_INVITED = "team_invited"
    TEAM_REMOVED = "team_removed"
    COMMENT_ADDED = "comment_added"
    MENTION = "mention"
    SYSTEM = "system"


class Notification(Base):
    """Notification model for user notifications."""

    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    type: Mapped[NotificationType] = mapped_column(Enum(NotificationType))
    title: Mapped[str] = mapped_column(String(255))
    message: Mapped[str] = mapped_column(Text)

    # Related entity
    related_task_id: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )
    related_team_id: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )

    # Status
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    read_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="notifications")

    def __repr__(self) -> str:
        return f"<Notification(id={self.id}, type={self.type}, user_id={self.user_id})>"
