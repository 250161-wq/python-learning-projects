"""Authentication endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import create_access_token, create_refresh_token, decode_token
from app.core.exceptions import AuthenticationError, ConflictError
from app.schemas.user import UserCreate, UserResponse, Token, UserLogin
from app.services.user_service import UserService

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """Register a new user."""
    user_service = UserService(db)
    try:
        user = await user_service.create(user_data)
        return user
    except ConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message,
        )


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """Login and get access token."""
    user_service = UserService(db)
    try:
        user = await user_service.authenticate(
            username=form_data.username,
            password=form_data.password,
        )
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        subject=user.id,
        additional_claims={"role": user.role.value},
    )
    refresh_token = create_refresh_token(subject=user.id)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/login/json", response_model=Token)
async def login_json(
    user_data: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    """Login with JSON body and get access token."""
    user_service = UserService(db)
    try:
        user = await user_service.authenticate(
            username=user_data.username,
            password=user_data.password,
        )
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        subject=user.id,
        additional_claims={"role": user.role.value},
    )
    refresh_token = create_refresh_token(subject=user.id)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_db),
):
    """Refresh access token using refresh token."""
    payload = decode_token(refresh_token)
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    user_id = payload.get("sub")
    user_service = UserService(db)
    user = await user_service.get_by_id(int(user_id))

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    access_token = create_access_token(
        subject=user.id,
        additional_claims={"role": user.role.value},
    )
    new_refresh_token = create_refresh_token(subject=user.id)

    return Token(
        access_token=access_token,
        refresh_token=new_refresh_token,
    )
