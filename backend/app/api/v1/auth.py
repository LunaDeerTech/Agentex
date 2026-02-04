"""Authentication API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.auth import (
    RefreshTokenRequest,
    RegisterResponse,
    TokenResponse,
    UserLogin,
    UserRegister,
)
from app.services.auth import AuthService

router = APIRouter()


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with username, email, and password.",
)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db),
) -> RegisterResponse:
    """
    Register a new user.

    - **username**: 3-50 characters, alphanumeric, underscore, and hyphen only
    - **email**: Valid email address
    - **password**: Minimum 8 characters, must contain uppercase, lowercase, and digit

    Returns the created user and authentication tokens.
    """
    auth_service = AuthService(db)

    try:
        result = await auth_service.register(user_data)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="User login",
    description="Authenticate user with username and password, returns JWT tokens.",
)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """
    Authenticate user and return JWT tokens.

    - **username**: User's username
    - **password**: User's password

    Returns access token and refresh token.
    """
    auth_service = AuthService(db)

    try:
        tokens = await auth_service.login(credentials)
        return tokens
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
    description="Generate new access and refresh tokens using a valid refresh token.",
)
async def refresh_token(
    token_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """
    Refresh access token using a valid refresh token.

    - **refresh_token**: Valid refresh token

    Returns new access token and refresh token.
    """
    auth_service = AuthService(db)

    try:
        tokens = await auth_service.refresh_access_token(token_data.refresh_token)
        return tokens
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
