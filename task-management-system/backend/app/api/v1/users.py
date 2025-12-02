"""User management endpoints."""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import NotFoundError, ConflictError
from app.models.user import User, UserRole
from app.schemas.user import UserResponse, UserUpdate
from app.schemas.common import PaginatedResponse, MessageResponse
from app.services.user_service import UserService
from app.api.deps import get_current_user, require_admin

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    """Get current user information."""
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update current user information."""
    user_service = UserService(db)
    # Users can't change their own role
    if user_data.role and not current_user.is_superuser:
        user_data.role = None
    try:
        user = await user_service.update(current_user.id, user_data)
        return user
    except ConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message,
        )


@router.get("", response_model=PaginatedResponse[UserResponse])
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    role: Optional[UserRole] = None,
    is_active: Optional[bool] = None,
    current_user: User = Depends(require_admin()),
    db: AsyncSession = Depends(get_db),
):
    """List all users (admin only)."""
    user_service = UserService(db)
    skip = (page - 1) * page_size
    users, total = await user_service.list_users(
        skip=skip,
        limit=page_size,
        role=role,
        is_active=is_active,
    )
    total_pages = (total + page_size - 1) // page_size

    return PaginatedResponse(
        items=users,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get user by ID."""
    # Users can view their own profile, admins can view any
    if user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this user",
        )

    user_service = UserService(db)
    user = await user_service.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(require_admin()),
    db: AsyncSession = Depends(get_db),
):
    """Update a user (admin only)."""
    user_service = UserService(db)
    try:
        user = await user_service.update(user_id, user_data)
        return user
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    except ConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message,
        )


@router.delete("/{user_id}", response_model=MessageResponse)
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_admin()),
    db: AsyncSession = Depends(get_db),
):
    """Delete a user (admin only)."""
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account",
        )

    user_service = UserService(db)
    try:
        await user_service.delete(user_id)
        return MessageResponse(message="User deleted successfully")
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
