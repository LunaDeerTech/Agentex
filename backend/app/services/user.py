"""User service for profile and API key management."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import generate_api_key, get_password_hash, verify_password
from app.models.api_key import ApiKey
from app.models.user import User
from app.schemas.user import (
    ApiKeyCreateRequest,
    UserPasswordUpdateRequest,
    UserUpdateRequest,
)


class UserService:
    """Service for user profile and API key operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def update_profile(self, user: User, data: UserUpdateRequest) -> User:
        """Update user profile information."""
        if data.username and data.username != user.username:
            if await self._username_exists(data.username):
                raise ValueError("Username already exists")
            user.username = data.username

        if data.email and data.email != user.email:
            if await self._email_exists(data.email):
                raise ValueError("Email already exists")
            user.email = data.email

        if data.avatar_url is not None:
            user.avatar_url = data.avatar_url

        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def change_password(
        self, user: User, data: UserPasswordUpdateRequest
    ) -> None:
        """Change user password after verifying current password."""
        if not verify_password(data.current_password, user.hashed_password):
            raise ValueError("Current password is incorrect")

        user.hashed_password = get_password_hash(data.new_password)
        await self.db.commit()

    async def create_api_key(
        self, user: User, data: ApiKeyCreateRequest
    ) -> tuple[str, ApiKey]:
        """Create a new API key and return the raw key and model."""
        if await self._api_key_name_exists(user.id, data.name):
            raise ValueError("API key name already exists")

        raw_key, key_hash, key_prefix = generate_api_key()

        api_key = ApiKey(
            user_id=user.id,
            name=data.name,
            key_hash=key_hash,
            key_prefix=key_prefix,
            expires_at=data.expires_at,
        )

        self.db.add(api_key)
        await self.db.commit()
        await self.db.refresh(api_key)

        return raw_key, api_key

    async def list_api_keys(self, user: User) -> list[ApiKey]:
        """List API keys for the current user."""
        stmt = (
            select(ApiKey)
            .where(
                ApiKey.user_id == user.id,
                ApiKey.is_deleted.is_(False),
            )
            .order_by(ApiKey.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def delete_api_key(self, user: User, key_id: uuid.UUID) -> None:
        """Soft delete an API key by ID."""
        stmt = select(ApiKey).where(
            ApiKey.id == key_id,
            ApiKey.user_id == user.id,
            ApiKey.is_deleted.is_(False),
        )
        result = await self.db.execute(stmt)
        api_key = result.scalar_one_or_none()

        if not api_key:
            raise ValueError("API key not found")

        api_key.is_deleted = True
        api_key.deleted_at = datetime.now(UTC)
        await self.db.commit()

    async def _username_exists(self, username: str) -> bool:
        stmt = select(User.id).where(
            User.username == username,
            User.is_deleted.is_(False),
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def _email_exists(self, email: str) -> bool:
        stmt = select(User.id).where(
            User.email == email,
            User.is_deleted.is_(False),
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def _api_key_name_exists(self, user_id: uuid.UUID, name: str) -> bool:
        stmt = select(ApiKey.id).where(
            ApiKey.user_id == user_id,
            ApiKey.name == name,
            ApiKey.is_deleted.is_(False),
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None
