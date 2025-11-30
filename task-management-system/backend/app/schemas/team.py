"""Team-related Pydantic schemas."""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.models.team import TeamRole


class TeamBase(BaseModel):
    """Base team schema."""

    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None


class TeamCreate(BaseModel):
    """Schema for creating a new team."""

    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None


class TeamUpdate(TeamBase):
    """Schema for updating a team."""

    is_active: Optional[bool] = None


class TeamMemberCreate(BaseModel):
    """Schema for adding a team member."""

    user_id: int
    role: TeamRole = TeamRole.MEMBER


class TeamMemberResponse(BaseModel):
    """Schema for team member response."""

    id: int
    user_id: int
    username: str
    full_name: Optional[str]
    role: TeamRole
    joined_at: datetime

    class Config:
        from_attributes = True


class TeamResponse(BaseModel):
    """Schema for team response."""

    id: int
    name: str
    description: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    members_count: int = 0
    tasks_count: int = 0

    class Config:
        from_attributes = True


class TeamDetailResponse(TeamResponse):
    """Schema for detailed team response with members."""

    members: List[TeamMemberResponse] = []
