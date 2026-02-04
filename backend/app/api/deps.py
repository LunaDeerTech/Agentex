"""FastAPI dependencies for authentication and authorization."""

import uuid
from datetime import UTC, datetime
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_token, hash_api_key
from app.models.api_key import ApiKey
from app.models.user import User

# HTTP Bearer token security scheme
security = HTTPBearer(auto_error=False)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    api_key: Annotated[str | None, Depends(api_key_header)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """
    Get current user from JWT token in Authorization header.

    Args:
        credentials: HTTP Bearer token credentials
        db: Database session

    Returns:
        Current authenticated user

    Raises:
        HTTPException: 401 if token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if api_key:
        key_hash = hash_api_key(api_key)
        stmt = select(ApiKey).where(
            ApiKey.key_hash == key_hash,
            ApiKey.is_deleted.is_(False),
        )
        result = await db.execute(stmt)
        api_key_row = result.scalar_one_or_none()
        if not api_key_row:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key",
            )
        if api_key_row.expires_at and api_key_row.expires_at <= datetime.now(UTC):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key expired",
            )

        user = await db.get(User, api_key_row.user_id)
        if user is None or user.is_deleted:
            raise credentials_exception

        api_key_row.last_used_at = datetime.now(UTC)
        await db.commit()
        return user

    if not credentials:
        raise credentials_exception

    token = credentials.credentials

    try:
        payload = decode_token(token)
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception

        # Verify token type
        token_type: str = payload.get("type")
        if token_type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Parse user ID
        try:
            user_id = uuid.UUID(user_id_str)
        except ValueError as exc:
            raise credentials_exception from exc

    except JWTError as exc:
        raise credentials_exception from exc

    # Get user from database
    user = await db.get(User, user_id)
    if user is None or user.is_deleted:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    Get current active user.

    Args:
        current_user: Current authenticated user

    Returns:
        Current active user

    Raises:
        HTTPException: 403 if user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    return current_user


async def get_current_superuser(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    """
    Get current superuser.

    Args:
        current_user: Current active user

    Returns:
        Current superuser

    Raises:
        HTTPException: 403 if user is not a superuser
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return current_user


def require_permissions(*required_permissions: str):
    """
    Dependency factory for permission checking.

    Creates a dependency that verifies the current user has all required permissions.

    Args:
        *required_permissions: Permission names required (e.g., "users:create", "models:edit")

    Returns:
        Async dependency function

    Example:
        @router.post("/items", dependencies=[Depends(require_permissions("items:create"))])
        async def create_item(...):
            ...
    """

    async def permission_checker(
        current_user: Annotated[User, Depends(get_current_active_user)],
    ) -> User:
        """
        Check if user has required permissions.

        Args:
            current_user: Current active user

        Returns:
            User if authorized

        Raises:
            HTTPException: 403 if user lacks required permissions
        """
        # Superusers have all permissions
        if current_user.is_superuser:
            return current_user

        # Collect user's permissions from roles
        user_permissions = set()
        for role in current_user.roles:
            for permission in role.permissions:
                user_permissions.add(permission.name)

        # Check if user has all required permissions
        missing_permissions = set(required_permissions) - user_permissions

        if missing_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing permissions: {', '.join(missing_permissions)}",
            )

        return current_user

    return permission_checker


def require_any_permission(*required_permissions: str):
    """
    Dependency factory for checking if user has any of the required permissions.

    Creates a dependency that verifies the current user has at least one of the required permissions.

    Args:
        *required_permissions: Permission names (user needs at least one)

    Returns:
        Async dependency function

    Example:
        @router.get("/items", dependencies=[Depends(require_any_permission("items:view", "items:admin"))])
        async def list_items(...):
            ...
    """

    async def permission_checker(
        current_user: Annotated[User, Depends(get_current_active_user)],
    ) -> User:
        """
        Check if user has any of the required permissions.

        Args:
            current_user: Current active user

        Returns:
            User if authorized

        Raises:
            HTTPException: 403 if user lacks all required permissions
        """
        # Superusers have all permissions
        if current_user.is_superuser:
            return current_user

        # Collect user's permissions from roles
        user_permissions = set()
        for role in current_user.roles:
            for permission in role.permissions:
                user_permissions.add(permission.name)

        # Check if user has any of the required permissions
        has_permission = bool(set(required_permissions) & user_permissions)

        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of: {', '.join(required_permissions)}",
            )

        return current_user

    return permission_checker


# Optional user dependency (doesn't raise error if no token provided)
async def get_optional_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(
        HTTPBearer(auto_error=False)
    ),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    """
    Get current user if token is provided, otherwise return None.

    Useful for endpoints that work differently for authenticated vs anonymous users.

    Args:
        credentials: Optional HTTP Bearer token credentials
        db: Database session

    Returns:
        Current user or None if no valid token provided
    """
    if credentials is None:
        return None

    try:
        token = credentials.credentials
        payload = decode_token(token)
        user_id_str: str = payload.get("sub")

        if user_id_str is None:
            return None

        # Verify token type
        token_type: str = payload.get("type")
        if token_type != "access":
            return None

        # Parse user ID
        try:
            user_id = uuid.UUID(user_id_str)
        except ValueError:
            return None

        # Get user from database
        user = await db.get(User, user_id)
        if user is None or user.is_deleted or not user.is_active:
            return None

        return user

    except (JWTError, Exception):
        return None
