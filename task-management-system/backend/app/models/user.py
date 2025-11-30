"""User model for authentication and authorization."""
import enum
from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import String, Boolean, DateTime, Enum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.task import Task
    from app.models.team import TeamMember
    from app.models.notification import Notification


class UserRole(str, enum.Enum):
    """User roles for role-based access control."""

    ADMIN = "admin"
    MANAGER = "manager"
    MEMBER = "member"
    VIEWER = "viewer"


class User(Base):
    """User model for authentication and authorization."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole), default=UserRole.MEMBER, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    last_login: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    owned_tasks: Mapped[List["Task"]] = relationship(
        "Task",
        back_populates="owner",
        foreign_keys="Task.owner_id",
        cascade="all, delete-orphan",
    )
    assigned_tasks: Mapped[List["Task"]] = relationship(
        "Task",
        back_populates="assignee",
        foreign_keys="Task.assignee_id",
    )
    team_memberships: Mapped[List["TeamMember"]] = relationship(
        "TeamMember",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    notifications: Mapped[List["Notification"]] = relationship(
        "Notification",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username={self.username}, role={self.role})>"

    @property
    def is_admin(self) -> bool:
        """Check if user has admin privileges."""
        return self.role == UserRole.ADMIN or self.is_superuser

    @property
    def is_manager(self) -> bool:
        """Check if user has manager privileges."""
        return self.role in (UserRole.ADMIN, UserRole.MANAGER) or self.is_superuser
