"""User-related Pydantic schemas."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.user import UserRole


class UserBase(BaseModel):
    """Base user schema."""

    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    full_name: Optional[str] = Field(None, max_length=255)
    bio: Optional[str] = None
    avatar_url: Optional[str] = None


class UserCreate(BaseModel):
    """Schema for creating a new user."""

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=8, max_length=100)
    full_name: Optional[str] = Field(None, max_length=255)
    role: UserRole = UserRole.MEMBER

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate username contains only allowed characters."""
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError(
                "Username must contain only alphanumeric characters, underscores, and hyphens"
            )
        return v.lower()

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserUpdate(UserBase):
    """Schema for updating a user."""

    password: Optional[str] = Field(None, min_length=8, max_length=100)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    """Schema for user response."""

    id: int
    email: EmailStr
    username: str
    full_name: Optional[str]
    bio: Optional[str]
    avatar_url: Optional[str]
    role: UserRole
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime]

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """Schema for user login."""

    username: str  # Can be username or email
    password: str


class Token(BaseModel):
    """Schema for JWT token response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Schema for decoded JWT token payload."""

    sub: str
    exp: datetime
    type: str
    role: Optional[str] = None
