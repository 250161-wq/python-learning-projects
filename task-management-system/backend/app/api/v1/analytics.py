"""Analytics endpoints."""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.schemas.analytics import TaskAnalytics, TeamAnalytics, UserAnalytics
from app.services.analytics_service import AnalyticsService
from app.api.deps import get_current_user

router = APIRouter()


@router.get("/tasks", response_model=TaskAnalytics)
async def get_task_analytics(
    team_id: Optional[int] = None,
    days: int = Query(30, ge=7, le=365),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get task analytics for the current user or a specific team."""
    analytics_service = AnalyticsService(db)

    # Non-admins can only see their own analytics
    user_id = None if current_user.is_admin else current_user.id

    analytics = await analytics_service.get_task_analytics(
        user_id=user_id,
        team_id=team_id,
        days=days,
    )

    return analytics


@router.get("/teams/{team_id}", response_model=TeamAnalytics)
async def get_team_analytics(
    team_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get analytics for a specific team."""
    analytics_service = AnalyticsService(db)
    analytics = await analytics_service.get_team_analytics(team_id)

    if not analytics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found",
        )

    return analytics


@router.get("/users/me", response_model=UserAnalytics)
async def get_my_analytics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get analytics for the current user."""
    analytics_service = AnalyticsService(db)
    analytics = await analytics_service.get_user_analytics(current_user.id)

    if not analytics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return analytics


@router.get("/users/{user_id}", response_model=UserAnalytics)
async def get_user_analytics(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get analytics for a specific user (admin only or own data)."""
    if user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this user's analytics",
        )

    analytics_service = AnalyticsService(db)
    analytics = await analytics_service.get_user_analytics(user_id)

    if not analytics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return analytics
