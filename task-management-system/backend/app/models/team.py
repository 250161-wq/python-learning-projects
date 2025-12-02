"""Team model for team collaboration."""
import enum
from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import String, Text, DateTime, Enum, ForeignKey, Boolean, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.task import Task


class TeamRole(str, enum.Enum):
    """Team member roles."""

    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


class Team(Base):
    """Team model for team collaboration."""

    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    members: Mapped[List["TeamMember"]] = relationship(
        "TeamMember", back_populates="team", cascade="all, delete-orphan"
    )
    tasks: Mapped[List["Task"]] = relationship("Task", back_populates="team")

    def __repr__(self) -> str:
        return f"<Team(id={self.id}, name={self.name})>"


class TeamMember(Base):
    """Team membership model."""

    __tablename__ = "team_members"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    role: Mapped[TeamRole] = mapped_column(Enum(TeamRole), default=TeamRole.MEMBER)

    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    team: Mapped["Team"] = relationship("Team", back_populates="members")
    user: Mapped["User"] = relationship("User", back_populates="team_memberships")

    # Ensure unique membership per team
    __table_args__ = (
        UniqueConstraint("team_id", "user_id", name="uix_team_user"),
    )

    def __repr__(self) -> str:
        return f"<TeamMember(team_id={self.team_id}, user_id={self.user_id}, role={self.role})>"
