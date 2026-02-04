"""Test authentication dependencies."""

import uuid
from datetime import datetime, timedelta

import pytest
from fastapi import HTTPException, status
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import (
    get_current_active_user,
    get_current_superuser,
    get_current_user,
    get_optional_current_user,
    require_any_permission,
    require_permissions,
)
from app.core.config import get_settings
from app.core.security import create_access_token
from app.models import Permission, Role, RolePermission, User

settings = get_settings()

pytestmark = pytest.mark.asyncio


class MockCredentials:
    """Mock HTTPAuthorizationCredentials."""

    def __init__(self, token: str):
        self.credentials = token


class TestGetCurrentUser:
    """Test get_current_user dependency."""

    async def test_valid_token(self, db: AsyncSession, test_user: User):
        """Test with valid access token."""
        token = create_access_token({"sub": str(test_user.id)})
        credentials = MockCredentials(token)

        user = await get_current_user(credentials, db)

        assert user.id == test_user.id
        assert user.username == test_user.username

    async def test_invalid_token(self, db: AsyncSession):
        """Test with invalid token."""
        credentials = MockCredentials("invalid_token")

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials, db)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Could not validate credentials" in exc_info.value.detail

    async def test_expired_token(self, db: AsyncSession, test_user: User):
        """Test with expired token."""
        expired_token = jwt.encode(
            {
                "sub": str(test_user.id),
                "type": "access",
                "exp": datetime.utcnow() - timedelta(hours=1),
            },
            settings.SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )
        credentials = MockCredentials(expired_token)

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials, db)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_refresh_token_instead_of_access(
        self, db: AsyncSession, test_user: User
    ):
        """Test with refresh token (should fail)."""
        refresh_token = jwt.encode(
            {
                "sub": str(test_user.id),
                "type": "refresh",
                "exp": datetime.utcnow() + timedelta(days=7),
            },
            settings.SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )
        credentials = MockCredentials(refresh_token)

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials, db)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid token type" in exc_info.value.detail

    async def test_nonexistent_user(self, db: AsyncSession):
        """Test with token for non-existent user."""
        fake_user_id = uuid.uuid4()
        token = create_access_token({"sub": str(fake_user_id)})
        credentials = MockCredentials(token)

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials, db)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_deleted_user(self, db: AsyncSession, test_user: User):
        """Test with token for deleted user."""
        token = create_access_token({"sub": str(test_user.id)})

        # Soft delete user
        test_user.is_deleted = True
        await db.commit()

        credentials = MockCredentials(token)

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials, db)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_token_without_subject(self, db: AsyncSession):
        """Test with token missing subject."""
        token = jwt.encode(
            {
                "type": "access",
                "exp": datetime.utcnow() + timedelta(minutes=30),
            },
            settings.SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )
        credentials = MockCredentials(token)

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials, db)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_token_with_invalid_uuid(self, db: AsyncSession):
        """Test with token containing invalid UUID."""
        token = jwt.encode(
            {
                "sub": "not-a-uuid",
                "type": "access",
                "exp": datetime.utcnow() + timedelta(minutes=30),
            },
            settings.SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )
        credentials = MockCredentials(token)

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials, db)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED


class TestGetCurrentActiveUser:
    """Test get_current_active_user dependency."""

    async def test_active_user(self, test_user: User):
        """Test with active user."""
        user = await get_current_active_user(test_user)
        assert user.id == test_user.id

    async def test_inactive_user(self, inactive_user: User):
        """Test with inactive user."""
        with pytest.raises(HTTPException) as exc_info:
            await get_current_active_user(inactive_user)

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "Inactive user" in exc_info.value.detail


class TestGetCurrentSuperuser:
    """Test get_current_superuser dependency."""

    async def test_superuser(self, superuser: User):
        """Test with superuser."""
        user = await get_current_superuser(superuser)
        assert user.id == superuser.id
        assert user.is_superuser is True

    async def test_regular_user(self, test_user: User):
        """Test with regular user (not superuser)."""
        with pytest.raises(HTTPException) as exc_info:
            await get_current_superuser(test_user)

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "Not enough permissions" in exc_info.value.detail


class TestRequirePermissions:
    """Test require_permissions dependency factory."""

    async def test_superuser_has_all_permissions(self, superuser: User):
        """Test superuser bypasses permission check."""
        checker = require_permissions("users:create", "models:delete")
        user = await checker(superuser)
        assert user.id == superuser.id

    async def test_user_with_required_permission(
        self, db: AsyncSession, test_user_with_permission: User
    ):
        """Test user with required permission."""
        checker = require_permissions("test:view")
        user = await checker(test_user_with_permission)
        assert user.id == test_user_with_permission.id

    async def test_user_with_multiple_required_permissions(
        self, db: AsyncSession, test_user_with_permissions: User
    ):
        """Test user with all required permissions."""
        checker = require_permissions("test:view", "test:create")
        user = await checker(test_user_with_permissions)
        assert user.id == test_user_with_permissions.id

    async def test_user_missing_permission(self, test_user: User):
        """Test user missing required permission."""
        checker = require_permissions("admin:full_access")

        with pytest.raises(HTTPException) as exc_info:
            await checker(test_user)

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "Missing permissions" in exc_info.value.detail
        assert "admin:full_access" in exc_info.value.detail

    async def test_user_missing_some_permissions(
        self, db: AsyncSession, test_user_with_permission: User
    ):
        """Test user with some but not all required permissions."""
        checker = require_permissions("test:view", "admin:full_access")

        with pytest.raises(HTTPException) as exc_info:
            await checker(test_user_with_permission)

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "admin:full_access" in exc_info.value.detail


class TestRequireAnyPermission:
    """Test require_any_permission dependency factory."""

    async def test_superuser(self, superuser: User):
        """Test superuser bypasses permission check."""
        checker = require_any_permission("users:create", "models:delete")
        user = await checker(superuser)
        assert user.id == superuser.id

    async def test_user_with_one_of_required_permissions(
        self, db: AsyncSession, test_user_with_permission: User
    ):
        """Test user with one of the required permissions."""
        checker = require_any_permission("test:view", "admin:full_access")
        user = await checker(test_user_with_permission)
        assert user.id == test_user_with_permission.id

    async def test_user_with_none_of_required_permissions(self, test_user: User):
        """Test user with none of the required permissions."""
        checker = require_any_permission("admin:full_access", "superadmin:control")

        with pytest.raises(HTTPException) as exc_info:
            await checker(test_user)

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "Requires one of" in exc_info.value.detail


class TestGetOptionalCurrentUser:
    """Test get_optional_current_user dependency."""

    async def test_valid_token(self, db: AsyncSession, test_user: User):
        """Test with valid token."""
        token = create_access_token({"sub": str(test_user.id)})
        credentials = MockCredentials(token)

        user = await get_optional_current_user(credentials, db)

        assert user is not None
        assert user.id == test_user.id

    async def test_no_credentials(self, db: AsyncSession):
        """Test with no credentials provided."""
        user = await get_optional_current_user(None, db)
        assert user is None

    async def test_invalid_token(self, db: AsyncSession):
        """Test with invalid token (returns None instead of error)."""
        credentials = MockCredentials("invalid_token")

        user = await get_optional_current_user(credentials, db)

        assert user is None

    async def test_expired_token(self, db: AsyncSession, test_user: User):
        """Test with expired token (returns None)."""
        expired_token = jwt.encode(
            {
                "sub": str(test_user.id),
                "type": "access",
                "exp": datetime.utcnow() - timedelta(hours=1),
            },
            settings.SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )
        credentials = MockCredentials(expired_token)

        user = await get_optional_current_user(credentials, db)

        assert user is None

    async def test_inactive_user(self, db: AsyncSession, inactive_user: User):
        """Test with inactive user (returns None)."""
        token = create_access_token({"sub": str(inactive_user.id)})
        credentials = MockCredentials(token)

        user = await get_optional_current_user(credentials, db)

        assert user is None
