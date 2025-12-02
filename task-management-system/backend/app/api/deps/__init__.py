"""API dependencies for dependency injection."""
from typing import Optional

from fastapi import Depends, HTTPException, status, WebSocket
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_token
from app.core.exceptions import AuthenticationError, AuthorizationError
from app.models.user import User, UserRole
from app.services.user_service import UserService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Get the current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_token(token)
    if payload is None:
        raise credentials_exception

    user_id = payload.get("sub")
    token_type = payload.get("type")

    if user_id is None or token_type != "access":
        raise credentials_exception

    user_service = UserService(db)
    user = await user_service.get_by_id(int(user_id))

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is disabled",
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Ensure current user is active."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
        )
    return current_user


def require_roles(*roles: UserRole):
    """Dependency factory for role-based access control."""
    async def check_roles(current_user: User = Depends(get_current_user)) -> User:
        if current_user.is_superuser:
            return current_user
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user
    return check_roles


def require_admin():
    """Require admin role."""
    return require_roles(UserRole.ADMIN)


def require_manager_or_admin():
    """Require manager or admin role."""
    return require_roles(UserRole.ADMIN, UserRole.MANAGER)


async def get_optional_current_user(
    token: Optional[str] = Depends(OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    """Get current user if authenticated, otherwise return None."""
    if not token:
        return None
    try:
        return await get_current_user(token, db)
    except HTTPException:
        return None


async def get_current_user_ws(
    websocket: WebSocket,
    db: AsyncSession,
) -> Optional[User]:
    """Get current user from WebSocket connection."""
    token = websocket.query_params.get("token")
    if not token:
        return None

    payload = decode_token(token)
    if payload is None:
        return None

    user_id = payload.get("sub")
    if user_id is None:
        return None

    user_service = UserService(db)
    return await user_service.get_by_id(int(user_id))
