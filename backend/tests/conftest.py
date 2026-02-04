"""Pytest configuration and fixtures."""

import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_factory
from app.core.security import get_password_hash
from app.main import app
from app.models import Role, User


@pytest.fixture
async def client() -> AsyncClient:
    """Create an async test client."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac


@pytest.fixture
async def db() -> AsyncSession:
    """Provide a database session for tests."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@pytest.fixture
async def default_role(db: AsyncSession) -> Role:
    """Create or get default 'user' role."""
    from sqlalchemy import select

    stmt = select(Role).where(Role.name == "user")
    result = await db.execute(stmt)
    role = result.scalar_one_or_none()

    if not role:
        role = Role(
            name="user",
            display_name="User",
            description="Default user role",
            is_system=True,
        )
        db.add(role)
        await db.commit()
        await db.refresh(role)

    return role


@pytest.fixture
async def test_user(db: AsyncSession, default_role: Role) -> User:
    """Create a test user."""
    from app.models import UserRole

    user = User(
        username="testuser",
        email="testuser@example.com",
        hashed_password=get_password_hash("TestPass123"),
        is_active=True,
        is_superuser=False,
    )
    db.add(user)
    await db.flush()

    # Assign default role
    user_role = UserRole(user_id=user.id, role_id=default_role.id)
    db.add(user_role)

    await db.commit()
    await db.refresh(user)

    return user


@pytest.fixture
async def inactive_user(db: AsyncSession) -> User:
    """Create an inactive test user."""
    user = User(
        username="inactiveuser",
        email="inactive@example.com",
        hashed_password=get_password_hash("TestPass123"),
        is_active=False,
        is_superuser=False,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user


@pytest.fixture
async def superuser(db: AsyncSession, default_role: Role) -> User:
    """Create a superuser."""
    from app.models import UserRole

    user = User(
        username="admin",
        email="admin@example.com",
        hashed_password=get_password_hash("AdminPass123"),
        is_active=True,
        is_superuser=True,
    )
    db.add(user)
    await db.flush()

    # Assign default role
    user_role = UserRole(user_id=user.id, role_id=default_role.id)
    db.add(user_role)

    await db.commit()
    await db.refresh(user)

    return user


@pytest.fixture
async def test_permission(db: AsyncSession) -> Permission:
    """Create a test permission."""
    permission = Permission(
        module="test",
        action="view",
        name="test:view",
        description="Test view permission",
    )
    db.add(permission)
    await db.commit()
    await db.refresh(permission)

    return permission


@pytest.fixture
async def test_role_with_permission(
    db: AsyncSession, test_permission: Permission
) -> Role:
    """Create a test role with permission."""
    role = Role(
        name="test_role",
        display_name="Test Role",
        description="Role for testing permissions",
        is_system=False,
    )
    db.add(role)
    await db.flush()

    # Assign permission to role
    role_permission = RolePermission(
        role_id=role.id,
        permission_id=test_permission.id,
    )
    db.add(role_permission)

    await db.commit()
    await db.refresh(role)

    return role


@pytest.fixture
async def test_user_with_permission(
    db: AsyncSession, test_role_with_permission: Role
) -> User:
    """Create a test user with a specific permission."""
    from app.models import UserRole

    user = User(
        username="permuser",
        email="permuser@example.com",
        hashed_password=get_password_hash("TestPass123"),
        is_active=True,
        is_superuser=False,
    )
    db.add(user)
    await db.flush()

    # Assign role with permission
    user_role = UserRole(user_id=user.id, role_id=test_role_with_permission.id)
    db.add(user_role)

    await db.commit()
    await db.refresh(user)

    return user


@pytest.fixture
async def test_user_with_permissions(db: AsyncSession) -> User:
    """Create a test user with multiple permissions."""
    from app.models import UserRole

    # Create permissions
    perm1 = Permission(
        module="test",
        action="view",
        name="test:view",
        description="Test view",
    )
    perm2 = Permission(
        module="test",
        action="create",
        name="test:create",
        description="Test create",
    )
    db.add(perm1)
    db.add(perm2)
    await db.flush()

    # Create role with permissions
    role = Role(
        name="multi_perm_role",
        display_name="Multi Permission Role",
        is_system=False,
    )
    db.add(role)
    await db.flush()

    role_perm1 = RolePermission(role_id=role.id, permission_id=perm1.id)
    role_perm2 = RolePermission(role_id=role.id, permission_id=perm2.id)
    db.add(role_perm1)
    db.add(role_perm2)

    # Create user
    user = User(
        username="multiuser",
        email="multiuser@example.com",
        hashed_password=get_password_hash("TestPass123"),
        is_active=True,
        is_superuser=False,
    )
    db.add(user)
    await db.flush()

    # Assign role
    user_role = UserRole(user_id=user.id, role_id=role.id)
    db.add(user_role)

    await db.commit()
    await db.refresh(user)

    return user
