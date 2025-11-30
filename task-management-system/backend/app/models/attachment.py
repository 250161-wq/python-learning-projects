"""Attachment model for file attachments."""
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.task import Task


class Attachment(Base):
    """Attachment model for task file attachments."""

    __tablename__ = "attachments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"), index=True)
    uploaded_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    filename: Mapped[str] = mapped_column(String(255))
    original_filename: Mapped[str] = mapped_column(String(255))
    file_path: Mapped[str] = mapped_column(String(500))
    file_size: Mapped[int] = mapped_column(Integer)
    content_type: Mapped[str] = mapped_column(String(100))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    task: Mapped["Task"] = relationship("Task", back_populates="attachments")

    def __repr__(self) -> str:
        return f"<Attachment(id={self.id}, filename={self.filename}, task_id={self.task_id})>"
