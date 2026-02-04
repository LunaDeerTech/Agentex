"""Authentication service for user registration and login."""

import uuid
from datetime import timedelta

from jose import JWTError
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from app.models import Role, User, UserRole
from app.schemas.auth import (
    RegisterResponse,
    TokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
)

settings = get_settings()


class AuthService:
    """Service for authentication operations."""

    def __init__(self, db: AsyncSession):
        """Initialize auth service with database session."""
        self.db = db

    async def register(self, user_data: UserRegister) -> RegisterResponse:
        """
        Register a new user.

        Args:
            user_data: User registration data

        Returns:
            RegisterResponse with user info and tokens

        Raises:
            ValueError: If username or email already exists
        """
        # Check if username or email already exists
        stmt = select(User).where(
            or_(
                User.username == user_data.username,
                User.email == user_data.email,
            ),
            User.is_deleted == False,
        )
        result = await self.db.execute(stmt)
        existing_user = result.scalar_one_or_none()

        if existing_user:
            if existing_user.username == user_data.username:
                raise ValueError("Username already exists")
            if existing_user.email == user_data.email:
                raise ValueError("Email already exists")

        # Create new user
        user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=get_password_hash(user_data.password),
            is_active=True,
            is_superuser=False,
        )
        self.db.add(user)
        await self.db.flush()

        # Assign default "user" role
        stmt = select(Role).where(Role.name == "user", Role.is_deleted == False)
        result = await self.db.execute(stmt)
        default_role = result.scalar_one_or_none()

        if default_role:
            user_role = UserRole(user_id=user.id, role_id=default_role.id)
            self.db.add(user_role)

        await self.db.commit()
        await self.db.refresh(user)

        # Generate tokens
        tokens = self._generate_tokens(user)

        return RegisterResponse(
            user=UserResponse.model_validate(user),
            tokens=tokens,
        )

    async def login(self, credentials: UserLogin) -> TokenResponse:
        """
        Authenticate user and generate tokens.

        Args:
            credentials: User login credentials

        Returns:
            TokenResponse with access and refresh tokens

        Raises:
            ValueError: If credentials are invalid
        """
        # Find user by username
        stmt = select(User).where(
            User.username == credentials.username,
            User.is_deleted == False,
        )
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            raise ValueError("Invalid username or password")

        # Verify password
        if not verify_password(credentials.password, user.hashed_password):
            raise ValueError("Invalid username or password")

        # Check if user is active
        if not user.is_active:
            raise ValueError("User account is inactive")

        # Update last login time
        from datetime import datetime

        user.last_login_at = datetime.utcnow()
        await self.db.commit()

        # Generate tokens
        return self._generate_tokens(user)

    async def refresh_access_token(self, refresh_token: str) -> TokenResponse:
        """
        Generate new access token from refresh token.

        Args:
            refresh_token: Valid refresh token

        Returns:
            TokenResponse with new access and refresh tokens

        Raises:
            ValueError: If refresh token is invalid or expired
        """
        try:
            payload = decode_token(refresh_token)
        except JWTError:
            raise ValueError("Invalid or expired refresh token")

        # Verify token type
        if payload.get("type") != "refresh":
            raise ValueError("Invalid token type")

        # Get user ID from payload
        user_id_str = payload.get("sub")
        if not user_id_str:
            raise ValueError("Invalid token payload")

        try:
            user_id = uuid.UUID(user_id_str)
        except ValueError:
            raise ValueError("Invalid user ID in token")

        # Get user from database
        user = await self.db.get(User, user_id)
        if not user or user.is_deleted:
            raise ValueError("User not found")

        if not user.is_active:
            raise ValueError("User account is inactive")

        # Generate new tokens
        return self._generate_tokens(user)

    def _generate_tokens(self, user: User) -> TokenResponse:
        """
        Generate access and refresh tokens for a user.

        Args:
            user: User model instance

        Returns:
            TokenResponse with tokens
        """
        token_data = {"sub": str(user.id)}

        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    async def get_user_by_id(self, user_id: uuid.UUID) -> User | None:
        """
        Get user by ID.

        Args:
            user_id: User UUID

        Returns:
            User model or None if not found
        """
        user = await self.db.get(User, user_id)
        if user and not user.is_deleted and user.is_active:
            return user
        return None
