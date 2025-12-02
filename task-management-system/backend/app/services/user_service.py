"""User service for user management operations."""
from datetime import datetime, timezone
from typing import Optional, List

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ConflictError, AuthenticationError
from app.core.security import get_password_hash, verify_password
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    """Service for user-related operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        result = await self.db.execute(
            select(User).where(User.email == email.lower())
        )
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        result = await self.db.execute(
            select(User).where(User.username == username.lower())
        )
        return result.scalar_one_or_none()

    async def get_by_username_or_email(self, identifier: str) -> Optional[User]:
        """Get user by username or email."""
        result = await self.db.execute(
            select(User).where(
                or_(
                    User.username == identifier.lower(),
                    User.email == identifier.lower()
                )
            )
        )
        return result.scalar_one_or_none()

    async def create(self, user_data: UserCreate) -> User:
        """Create a new user."""
        # Check for existing email
        existing_email = await self.get_by_email(user_data.email)
        if existing_email:
            raise ConflictError(
                message="Email already registered",
                details={"field": "email"}
            )

        # Check for existing username
        existing_username = await self.get_by_username(user_data.username)
        if existing_username:
            raise ConflictError(
                message="Username already taken",
                details={"field": "username"}
            )

        user = User(
            email=user_data.email.lower(),
            username=user_data.username.lower(),
            hashed_password=get_password_hash(user_data.password),
            full_name=user_data.full_name,
            role=user_data.role,
        )
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def update(self, user_id: int, user_data: UserUpdate) -> User:
        """Update an existing user."""
        user = await self.get_by_id(user_id)
        if not user:
            raise NotFoundError(message="User not found")

        update_data = user_data.model_dump(exclude_unset=True)

        if "password" in update_data and update_data["password"]:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
        elif "password" in update_data:
            del update_data["password"]

        if "email" in update_data:
            existing = await self.get_by_email(update_data["email"])
            if existing and existing.id != user_id:
                raise ConflictError(
                    message="Email already registered",
                    details={"field": "email"}
                )
            update_data["email"] = update_data["email"].lower()

        if "username" in update_data:
            existing = await self.get_by_username(update_data["username"])
            if existing and existing.id != user_id:
                raise ConflictError(
                    message="Username already taken",
                    details={"field": "username"}
                )
            update_data["username"] = update_data["username"].lower()

        for field, value in update_data.items():
            setattr(user, field, value)

        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def delete(self, user_id: int) -> bool:
        """Delete a user."""
        user = await self.get_by_id(user_id)
        if not user:
            raise NotFoundError(message="User not found")

        await self.db.delete(user)
        await self.db.flush()
        return True

    async def authenticate(self, username: str, password: str) -> User:
        """Authenticate a user with username/email and password."""
        user = await self.get_by_username_or_email(username)
        if not user:
            raise AuthenticationError(message="Invalid credentials")

        if not verify_password(password, user.hashed_password):
            raise AuthenticationError(message="Invalid credentials")

        if not user.is_active:
            raise AuthenticationError(message="User account is disabled")

        # Update last login
        user.last_login = datetime.now(timezone.utc)
        await self.db.flush()

        return user

    async def list_users(
        self,
        skip: int = 0,
        limit: int = 20,
        role: Optional[UserRole] = None,
        is_active: Optional[bool] = None,
    ) -> tuple[List[User], int]:
        """List users with filtering and pagination."""
        query = select(User)

        if role:
            query = query.where(User.role == role)
        if is_active is not None:
            query = query.where(User.is_active == is_active)

        # Get total count
        count_result = await self.db.execute(
            select(User.id).where(
                *(
                    [User.role == role] if role else []
                ) + (
                    [User.is_active == is_active] if is_active is not None else []
                )
            )
        )
        total = len(count_result.all())

        # Get paginated results
        query = query.offset(skip).limit(limit).order_by(User.created_at.desc())
        result = await self.db.execute(query)
        users = result.scalars().all()

        return list(users), total
