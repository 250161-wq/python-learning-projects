"""Team collaboration endpoints."""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import NotFoundError, ConflictError, AuthorizationError
from app.models.user import User
from app.models.team import TeamRole
from app.schemas.team import (
    TeamCreate,
    TeamUpdate,
    TeamResponse,
    TeamDetailResponse,
    TeamMemberCreate,
    TeamMemberResponse,
)
from app.schemas.common import PaginatedResponse, MessageResponse
from app.services.team_service import TeamService
from app.services.notification_service import NotificationService
from app.api.deps import get_current_user

router = APIRouter()


@router.post("", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
async def create_team(
    team_data: TeamCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new team."""
    team_service = TeamService(db)
    try:
        team = await team_service.create(team_data, current_user.id)
        return TeamResponse(
            id=team.id,
            name=team.name,
            description=team.description,
            is_active=team.is_active,
            created_at=team.created_at,
            updated_at=team.updated_at,
            members_count=len(team.members),
            tasks_count=0,
        )
    except ConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message,
        )


@router.get("", response_model=PaginatedResponse[TeamResponse])
async def list_teams(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    include_inactive: bool = False,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List teams the user has access to."""
    team_service = TeamService(db)
    teams, total = await team_service.list_teams(
        current_user=current_user,
        page=page,
        page_size=page_size,
        include_inactive=include_inactive,
    )

    total_pages = (total + page_size - 1) // page_size

    return PaginatedResponse(
        items=[
            TeamResponse(
                id=team.id,
                name=team.name,
                description=team.description,
                is_active=team.is_active,
                created_at=team.created_at,
                updated_at=team.updated_at,
                members_count=len(team.members) if team.members else 0,
                tasks_count=len(team.tasks) if team.tasks else 0,
            )
            for team in teams
        ],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{team_id}", response_model=TeamDetailResponse)
async def get_team(
    team_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get team details with members."""
    team_service = TeamService(db)
    team = await team_service.get_by_id(team_id, include_members=True)

    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found",
        )

    return TeamDetailResponse(
        id=team.id,
        name=team.name,
        description=team.description,
        is_active=team.is_active,
        created_at=team.created_at,
        updated_at=team.updated_at,
        members_count=len(team.members),
        tasks_count=len(team.tasks) if team.tasks else 0,
        members=[
            TeamMemberResponse(
                id=member.id,
                user_id=member.user_id,
                username=member.user.username,
                full_name=member.user.full_name,
                role=member.role,
                joined_at=member.joined_at,
            )
            for member in team.members
        ],
    )


@router.patch("/{team_id}", response_model=TeamResponse)
async def update_team(
    team_id: int,
    team_data: TeamUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a team."""
    team_service = TeamService(db)
    try:
        team = await team_service.update(team_id, team_data, current_user)
        return TeamResponse(
            id=team.id,
            name=team.name,
            description=team.description,
            is_active=team.is_active,
            created_at=team.created_at,
            updated_at=team.updated_at,
            members_count=len(team.members) if team.members else 0,
            tasks_count=len(team.tasks) if team.tasks else 0,
        )
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found",
        )
    except AuthorizationError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.message,
        )
    except ConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message,
        )


@router.delete("/{team_id}", response_model=MessageResponse)
async def delete_team(
    team_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a team."""
    team_service = TeamService(db)
    try:
        await team_service.delete(team_id, current_user)
        return MessageResponse(message="Team deleted successfully")
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found",
        )
    except AuthorizationError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.message,
        )


@router.post("/{team_id}/members", response_model=TeamMemberResponse, status_code=status.HTTP_201_CREATED)
async def add_team_member(
    team_id: int,
    member_data: TeamMemberCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add a member to a team."""
    team_service = TeamService(db)
    notification_service = NotificationService(db)

    try:
        member = await team_service.add_member(team_id, member_data, current_user)

        # Get team for notification
        team = await team_service.get_by_id(team_id)

        # Notify the added user
        if member.user_id != current_user.id:
            await notification_service.notify_team_invited(
                team_id=team_id,
                team_name=team.name,
                user_id=member.user_id,
                inviter_name=current_user.username,
            )

        # Fetch user info for response
        from app.services.user_service import UserService
        user_service = UserService(db)
        user = await user_service.get_by_id(member.user_id)

        return TeamMemberResponse(
            id=member.id,
            user_id=member.user_id,
            username=user.username,
            full_name=user.full_name,
            role=member.role,
            joined_at=member.joined_at,
        )
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found",
        )
    except AuthorizationError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.message,
        )
    except ConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message,
        )


@router.delete("/{team_id}/members/{user_id}", response_model=MessageResponse)
async def remove_team_member(
    team_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove a member from a team."""
    team_service = TeamService(db)
    try:
        await team_service.remove_member(team_id, user_id, current_user)
        return MessageResponse(message="Team member removed successfully")
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )
    except AuthorizationError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.message,
        )
    except ConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message,
        )


@router.patch("/{team_id}/members/{user_id}/role", response_model=TeamMemberResponse)
async def update_member_role(
    team_id: int,
    user_id: int,
    role: TeamRole,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a team member's role."""
    team_service = TeamService(db)
    try:
        member = await team_service.update_member_role(team_id, user_id, role, current_user)

        # Fetch user info for response
        from app.services.user_service import UserService
        user_service = UserService(db)
        user = await user_service.get_by_id(member.user_id)

        return TeamMemberResponse(
            id=member.id,
            user_id=member.user_id,
            username=user.username,
            full_name=user.full_name,
            role=member.role,
            joined_at=member.joined_at,
        )
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )
    except AuthorizationError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.message,
        )
    except ConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message,
        )
