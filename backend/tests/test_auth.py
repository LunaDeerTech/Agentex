"""Test authentication API endpoints and services."""

import uuid
from datetime import datetime, timedelta

import pytest
from fastapi import status
from httpx import AsyncClient
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import create_refresh_token, get_password_hash, verify_password
from app.models import Role, User
from app.services.auth import AuthService

settings = get_settings()

pytestmark = pytest.mark.asyncio


class TestPasswordHashing:
    """Test password hashing utilities."""

    def test_hash_password(self):
        """Test password hashing."""
        password = "TestPassword123"
        hashed = get_password_hash(password)

        assert hashed != password
        assert len(hashed) > 0
        assert hashed.startswith("$2")  # bcrypt prefix ($2a$, $2b$, etc.)

    def test_verify_password_correct(self):
        """Test password verification with correct password."""
        password = "TestPassword123"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password."""
        password = "TestPassword123"
        wrong_password = "WrongPassword123"
        hashed = get_password_hash(password)

        assert verify_password(wrong_password, hashed) is False


class TestAuthService:
    """Test authentication service."""

    async def test_register_success(self, db: AsyncSession, default_role: Role):
        """Test successful user registration."""
        auth_service = AuthService(db)

        from app.schemas.auth import UserRegister

        user_data = UserRegister(
            username="testuser",
            email="test@example.com",
            password="TestPass123",
        )

        result = await auth_service.register(user_data)

        assert result.user.username == "testuser"
        assert result.user.email == "test@example.com"
        assert result.user.is_active is True
        assert result.user.is_superuser is False
        assert result.tokens.access_token is not None
        assert result.tokens.refresh_token is not None
        assert result.tokens.token_type == "bearer"

    async def test_register_duplicate_username(self, db: AsyncSession, test_user: User):
        """Test registration with duplicate username."""
        auth_service = AuthService(db)

        from app.schemas.auth import UserRegister

        user_data = UserRegister(
            username=test_user.username,
            email="different@example.com",
            password="TestPass123",
        )

        with pytest.raises(ValueError, match="Username already exists"):
            await auth_service.register(user_data)

    async def test_register_duplicate_email(self, db: AsyncSession, test_user: User):
        """Test registration with duplicate email."""
        auth_service = AuthService(db)

        from app.schemas.auth import UserRegister

        user_data = UserRegister(
            username="differentuser",
            email=test_user.email,
            password="TestPass123",
        )

        with pytest.raises(ValueError, match="Email already exists"):
            await auth_service.register(user_data)

    async def test_login_success(self, db: AsyncSession, test_user: User):
        """Test successful login."""
        auth_service = AuthService(db)

        from app.schemas.auth import UserLogin

        credentials = UserLogin(
            username=test_user.username,
            password="TestPass123",  # From fixture
        )

        tokens = await auth_service.login(credentials)

        assert tokens.access_token is not None
        assert tokens.refresh_token is not None
        assert tokens.token_type == "bearer"
        assert tokens.expires_in == settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60

    async def test_login_wrong_password(self, db: AsyncSession, test_user: User):
        """Test login with incorrect password."""
        auth_service = AuthService(db)

        from app.schemas.auth import UserLogin

        credentials = UserLogin(
            username=test_user.username,
            password="WrongPassword123",
        )

        with pytest.raises(ValueError, match="Invalid username or password"):
            await auth_service.login(credentials)

    async def test_login_nonexistent_user(self, db: AsyncSession):
        """Test login with non-existent user."""
        auth_service = AuthService(db)

        from app.schemas.auth import UserLogin

        credentials = UserLogin(
            username="nonexistent",
            password="TestPass123",
        )

        with pytest.raises(ValueError, match="Invalid username or password"):
            await auth_service.login(credentials)

    async def test_login_inactive_user(self, db: AsyncSession, inactive_user: User):
        """Test login with inactive user."""
        auth_service = AuthService(db)

        from app.schemas.auth import UserLogin

        credentials = UserLogin(
            username=inactive_user.username,
            password="TestPass123",
        )

        with pytest.raises(ValueError, match="User account is inactive"):
            await auth_service.login(credentials)

    async def test_refresh_token_success(self, db: AsyncSession, test_user: User):
        """Test successful token refresh."""
        auth_service = AuthService(db)

        # Create a valid refresh token
        refresh_token = create_refresh_token({"sub": str(test_user.id)})

        tokens = await auth_service.refresh_access_token(refresh_token)

        assert tokens.access_token is not None
        assert tokens.refresh_token is not None
        assert tokens.token_type == "bearer"

    async def test_refresh_token_invalid(self, db: AsyncSession):
        """Test refresh with invalid token."""
        auth_service = AuthService(db)

        with pytest.raises(ValueError, match="Invalid or expired refresh token"):
            await auth_service.refresh_access_token("invalid_token")

    async def test_refresh_token_expired(self, db: AsyncSession, test_user: User):
        """Test refresh with expired token."""
        auth_service = AuthService(db)

        # Create an expired token
        expired_token = jwt.encode(
            {
                "sub": str(test_user.id),
                "type": "refresh",
                "exp": datetime.utcnow() - timedelta(days=1),
            },
            settings.SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )

        with pytest.raises(ValueError, match="Invalid or expired refresh token"):
            await auth_service.refresh_access_token(expired_token)

    async def test_refresh_token_wrong_type(self, db: AsyncSession, test_user: User):
        """Test refresh with access token instead of refresh token."""
        auth_service = AuthService(db)

        # Create an access token
        access_token = jwt.encode(
            {
                "sub": str(test_user.id),
                "type": "access",
                "exp": datetime.utcnow() + timedelta(minutes=30),
            },
            settings.SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )

        with pytest.raises(ValueError, match="Invalid token type"):
            await auth_service.refresh_access_token(access_token)


class TestAuthAPI:
    """Test authentication API endpoints."""

    async def test_register_api_success(self, client: AsyncClient, default_role: Role):
        """Test POST /api/v1/auth/register success."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "SecurePass123",
            },
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["user"]["username"] == "newuser"
        assert data["user"]["email"] == "newuser@example.com"
        assert "access_token" in data["tokens"]
        assert "refresh_token" in data["tokens"]

    async def test_register_api_duplicate_username(
        self, client: AsyncClient, test_user: User
    ):
        """Test POST /api/v1/auth/register with duplicate username."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": test_user.username,
                "email": "different@example.com",
                "password": "SecurePass123",
            },
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Username already exists" in response.json()["detail"]

    async def test_register_api_invalid_password(self, client: AsyncClient):
        """Test POST /api/v1/auth/register with weak password."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "weak",  # Too short, no uppercase, no digits
            },
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_login_api_success(self, client: AsyncClient, test_user: User):
        """Test POST /api/v1/auth/login success."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "username": test_user.username,
                "password": "TestPass123",
            },
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_api_wrong_password(self, client: AsyncClient, test_user: User):
        """Test POST /api/v1/auth/login with wrong password."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "username": test_user.username,
                "password": "WrongPassword",
            },
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid username or password" in response.json()["detail"]

    async def test_refresh_api_success(self, client: AsyncClient, test_user: User):
        """Test POST /api/v1/auth/refresh success."""
        # First login to get tokens
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "username": test_user.username,
                "password": "TestPass123",
            },
        )
        refresh_token = login_response.json()["refresh_token"]

        # Use refresh token
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    async def test_refresh_api_invalid_token(self, client: AsyncClient):
        """Test POST /api/v1/auth/refresh with invalid token."""
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid_token"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
