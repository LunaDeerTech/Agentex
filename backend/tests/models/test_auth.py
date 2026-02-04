"""Test authentication models."""

import uuid
from datetime import datetime

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Permission, Role, RolePermission, User, UserRole


@pytest.mark.asyncio
class TestUserModel:
    """Test User model."""

    async def test_create_user(self, db: AsyncSession):
        """Test creating a user."""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashedpassword123",
            is_active=True,
            is_superuser=False,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

        assert user.id is not None
        assert isinstance(user.id, uuid.UUID)
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.is_active is True
        assert user.is_superuser is False
        assert user.is_deleted is False
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)

    async def test_user_unique_username(self, db: AsyncSession):
        """Test username uniqueness constraint."""
        user1 = User(
            username="duplicate",
            email="user1@example.com",
            hashed_password="password",
        )
        db.add(user1)
        await db.commit()

        user2 = User(
            username="duplicate",
            email="user2@example.com",
            hashed_password="password",
        )
        db.add(user2)

        with pytest.raises(Exception):  # IntegrityError
            await db.commit()

    async def test_user_unique_email(self, db: AsyncSession):
        """Test email uniqueness constraint."""
        user1 = User(
            username="user1",
            email="duplicate@example.com",
            hashed_password="password",
        )
        db.add(user1)
        await db.commit()

        user2 = User(
            username="user2",
            email="duplicate@example.com",
            hashed_password="password",
        )
        db.add(user2)

        with pytest.raises(Exception):  # IntegrityError
            await db.commit()


@pytest.mark.asyncio
class TestRoleModel:
    """Test Role model."""

    async def test_create_role(self, db: AsyncSession):
        """Test creating a role."""
        role = Role(
            name="test_role",
            display_name="Test Role",
            description="Test role description",
            is_system=False,
        )
        db.add(role)
        await db.commit()
        await db.refresh(role)

        assert role.id is not None
        assert role.name == "test_role"
        assert role.display_name == "Test Role"
        assert role.is_system is False
        assert role.is_deleted is False


@pytest.mark.asyncio
class TestPermissionModel:
    """Test Permission model."""

    async def test_create_permission(self, db: AsyncSession):
        """Test creating a permission."""
        permission = Permission(
            module="test",
            action="view",
            name="test:view",
            description="View test module",
        )
        db.add(permission)
        await db.commit()
        await db.refresh(permission)

        assert permission.id is not None
        assert permission.module == "test"
        assert permission.action == "view"
        assert permission.name == "test:view"


@pytest.mark.asyncio
class TestUserRoleRelationship:
    """Test User-Role relationship."""

    async def test_assign_role_to_user(self, db: AsyncSession):
        """Test assigning a role to a user."""
        # Create user
        user = User(
            username="roletest",
            email="roletest@example.com",
            hashed_password="password",
        )
        db.add(user)

        # Create role
        role = Role(
            name="test_role",
            display_name="Test Role",
        )
        db.add(role)
        await db.commit()

        # Assign role to user
        user_role = UserRole(
            user_id=user.id,
            role_id=role.id,
        )
        db.add(user_role)
        await db.commit()

        # Verify relationship
        await db.refresh(user)
        assert len(user.roles) == 1
        assert user.roles[0].name == "test_role"


@pytest.mark.asyncio
class TestRolePermissionRelationship:
    """Test Role-Permission relationship."""

    async def test_assign_permission_to_role(self, db: AsyncSession):
        """Test assigning a permission to a role."""
        # Create role
        role = Role(
            name="test_role",
            display_name="Test Role",
        )
        db.add(role)

        # Create permission
        permission = Permission(
            module="test",
            action="view",
            name="test:view",
        )
        db.add(permission)
        await db.commit()

        # Assign permission to role
        role_permission = RolePermission(
            role_id=role.id,
            permission_id=permission.id,
        )
        db.add(role_permission)
        await db.commit()

        # Verify relationship
        await db.refresh(role)
        assert len(role.permissions) == 1
        assert role.permissions[0].name == "test:view"
