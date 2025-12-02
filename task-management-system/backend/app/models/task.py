"""Task model for task management."""
import enum
from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import (
    String,
    Text,
    DateTime,
    Enum,
    Integer,
    ForeignKey,
    Boolean,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.team import Team
    from app.models.attachment import Attachment


class TaskPriority(str, enum.Enum):
    """Task priority levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskStatus(str, enum.Enum):
    """Task status values."""

    TODO = "todo"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class TaskCategory(str, enum.Enum):
    """Task categories."""

    BUG = "bug"
    FEATURE = "feature"
    IMPROVEMENT = "improvement"
    DOCUMENTATION = "documentation"
    MAINTENANCE = "maintenance"
    RESEARCH = "research"
    OTHER = "other"


class Task(Base):
    """Task model for task management."""

    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    priority: Mapped[TaskPriority] = mapped_column(
        Enum(TaskPriority), default=TaskPriority.MEDIUM
    )
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus), default=TaskStatus.TODO
    )
    category: Mapped[TaskCategory] = mapped_column(
        Enum(TaskCategory), default=TaskCategory.OTHER
    )

    # Task metadata
    estimated_hours: Mapped[Optional[float]] = mapped_column(nullable=True)
    actual_hours: Mapped[Optional[float]] = mapped_column(nullable=True)
    progress_percent: Mapped[int] = mapped_column(Integer, default=0)

    # Dates
    due_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Flags
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)

    # Foreign keys
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    assignee_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )
    team_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("teams.id"), nullable=True, index=True
    )
    parent_task_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("tasks.id"), nullable=True
    )

    # Relationships
    owner: Mapped["User"] = relationship(
        "User", back_populates="owned_tasks", foreign_keys=[owner_id]
    )
    assignee: Mapped[Optional["User"]] = relationship(
        "User", back_populates="assigned_tasks", foreign_keys=[assignee_id]
    )
    team: Mapped[Optional["Team"]] = relationship("Team", back_populates="tasks")
    attachments: Mapped[List["Attachment"]] = relationship(
        "Attachment", back_populates="task", cascade="all, delete-orphan"
    )
    subtasks: Mapped[List["Task"]] = relationship(
        "Task", back_populates="parent_task", cascade="all, delete-orphan"
    )
    parent_task: Mapped[Optional["Task"]] = relationship(
        "Task", back_populates="subtasks", remote_side=[id]
    )

    # Indexes for common queries
    __table_args__ = (
        Index("ix_tasks_status_priority", "status", "priority"),
        Index("ix_tasks_owner_status", "owner_id", "status"),
        Index("ix_tasks_due_date", "due_date"),
    )

    def __repr__(self) -> str:
        return f"<Task(id={self.id}, title={self.title}, status={self.status})>"

    @property
    def is_overdue(self) -> bool:
        """Check if task is overdue."""
        if self.due_date and self.status not in (
            TaskStatus.COMPLETED,
            TaskStatus.ARCHIVED,
        ):
            return datetime.now(timezone.utc) > self.due_date
        return False
