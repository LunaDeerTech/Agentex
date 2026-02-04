"""LLM Model service for managing model configurations."""

import time
import uuid
from datetime import UTC, datetime
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.encryption import decrypt_api_key, encrypt_api_key, mask_api_key
from app.integrations.llm import LLMClientFactory, LLMConfig
from app.models.llm_model import LLMModel
from app.models.user import User
from app.schemas.llm_model import (
    LLMModelCreateRequest,
    LLMModelResponse,
    LLMModelTestResponse,
    LLMModelUpdateRequest,
)


class LLMModelService:
    """Service for LLM model configuration operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_model(self, user: User, data: LLMModelCreateRequest) -> LLMModel:
        """
        Create a new LLM model configuration.

        Args:
            user: The user creating the model
            data: Model creation request data

        Returns:
            The created LLM model
        """
        # If this is set as default, unset other defaults for this user
        if data.is_default:
            await self._unset_default_models(user.id)

        # Encrypt the API key
        encrypted_key = encrypt_api_key(data.api_key)

        model = LLMModel(
            user_id=user.id,
            name=data.name,
            provider=data.provider.value,
            model_id=data.model_id,
            base_url=data.base_url,
            api_key_encrypted=encrypted_key,
            max_tokens=data.max_tokens,
            temperature=data.temperature,
            top_p=data.top_p,
            is_default=data.is_default,
            description=data.description,
        )

        self.db.add(model)
        await self.db.commit()
        await self.db.refresh(model)

        return model

    async def list_models(self, user: User) -> list[LLMModel]:
        """
        List all LLM model configurations for a user.

        Args:
            user: The user whose models to list

        Returns:
            List of LLM models
        """
        stmt = (
            select(LLMModel)
            .where(
                LLMModel.user_id == user.id,
                LLMModel.is_deleted.is_(False),
            )
            .order_by(LLMModel.is_default.desc(), LLMModel.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_model(self, user: User, model_id: uuid.UUID) -> Optional[LLMModel]:
        """
        Get a specific LLM model configuration.

        Args:
            user: The user requesting the model
            model_id: The model ID

        Returns:
            The LLM model or None if not found
        """
        stmt = select(LLMModel).where(
            LLMModel.id == model_id,
            LLMModel.user_id == user.id,
            LLMModel.is_deleted.is_(False),
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def update_model(
        self, user: User, model_id: uuid.UUID, data: LLMModelUpdateRequest
    ) -> Optional[LLMModel]:
        """
        Update an LLM model configuration.

        Args:
            user: The user updating the model
            model_id: The model ID to update
            data: Update request data

        Returns:
            The updated model or None if not found
        """
        model = await self.get_model(user, model_id)
        if not model:
            return None

        # Handle default flag
        if data.is_default is True and not model.is_default:
            await self._unset_default_models(user.id)

        # Update fields if provided
        if data.name is not None:
            model.name = data.name
        if data.model_id is not None:
            model.model_id = data.model_id
        if data.api_key is not None:
            model.api_key_encrypted = encrypt_api_key(data.api_key)
        if data.base_url is not None:
            model.base_url = data.base_url if data.base_url else None
        if data.max_tokens is not None:
            model.max_tokens = data.max_tokens
        if data.temperature is not None:
            model.temperature = data.temperature
        if data.top_p is not None:
            model.top_p = data.top_p
        if data.is_enabled is not None:
            model.is_enabled = data.is_enabled
        if data.is_default is not None:
            model.is_default = data.is_default
        if data.description is not None:
            model.description = data.description

        await self.db.commit()
        await self.db.refresh(model)

        return model

    async def delete_model(self, user: User, model_id: uuid.UUID) -> bool:
        """
        Soft delete an LLM model configuration.

        Args:
            user: The user deleting the model
            model_id: The model ID to delete

        Returns:
            True if deleted, False if not found
        """
        model = await self.get_model(user, model_id)
        if not model:
            return False

        model.is_deleted = True
        model.deleted_at = datetime.now(UTC)

        await self.db.commit()
        return True

    async def test_model(
        self, user: User, model_id: uuid.UUID, prompt: Optional[str] = None
    ) -> LLMModelTestResponse:
        """
        Test an LLM model configuration.

        Args:
            user: The user testing the model
            model_id: The model ID to test
            prompt: Optional test prompt

        Returns:
            Test result response
        """
        model = await self.get_model(user, model_id)
        if not model:
            return LLMModelTestResponse(
                success=False,
                message="Model not found",
            )

        if not model.is_enabled:
            return LLMModelTestResponse(
                success=False,
                message="Model is disabled",
            )

        try:
            # Decrypt the API key
            api_key = decrypt_api_key(model.api_key_encrypted)

            # Create LLM client
            config = LLMConfig(
                model_id=model.model_id,
                api_key=api_key,
                base_url=model.base_url,
                max_tokens=50,  # Small limit for test
                temperature=0,
            )
            client = LLMClientFactory.create(model.provider, config)

            # Test connection
            start_time = time.time()
            success, message, model_info = await client.test_connection()
            latency_ms = int((time.time() - start_time) * 1000)

            return LLMModelTestResponse(
                success=success,
                message=message,
                response_text=model_info.get("response") if model_info else None,
                latency_ms=latency_ms,
                model_info=model_info,
            )

        except Exception as e:
            return LLMModelTestResponse(
                success=False,
                message=f"Test failed: {str(e)}",
            )

    async def get_default_model(self, user: User) -> Optional[LLMModel]:
        """
        Get the user's default LLM model.

        Args:
            user: The user

        Returns:
            The default model or None
        """
        stmt = select(LLMModel).where(
            LLMModel.user_id == user.id,
            LLMModel.is_deleted.is_(False),
            LLMModel.is_enabled.is_(True),
            LLMModel.is_default.is_(True),
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def set_default_model(
        self, user: User, model_id: uuid.UUID
    ) -> Optional[LLMModel]:
        """
        Set a model as the default for the user.

        Args:
            user: The user
            model_id: The model ID to set as default

        Returns:
            The updated model or None if not found
        """
        model = await self.get_model(user, model_id)
        if not model:
            return None

        await self._unset_default_models(user.id)

        model.is_default = True
        await self.db.commit()
        await self.db.refresh(model)

        return model

    async def get_client_for_model(self, user: User, model_id: uuid.UUID):
        """
        Get an LLM client instance for a model.

        Args:
            user: The user
            model_id: The model ID

        Returns:
            Configured LLM client

        Raises:
            ValueError: If model not found or disabled
        """
        model = await self.get_model(user, model_id)
        if not model:
            raise ValueError("Model not found")
        if not model.is_enabled:
            raise ValueError("Model is disabled")

        api_key = decrypt_api_key(model.api_key_encrypted)

        config = LLMConfig(
            model_id=model.model_id,
            api_key=api_key,
            base_url=model.base_url,
            max_tokens=model.max_tokens,
            temperature=model.temperature,
            top_p=model.top_p,
        )

        return LLMClientFactory.create(model.provider, config)

    async def _unset_default_models(self, user_id: uuid.UUID) -> None:
        """Unset all default models for a user."""
        stmt = (
            update(LLMModel)
            .where(
                LLMModel.user_id == user_id,
                LLMModel.is_deleted.is_(False),
                LLMModel.is_default.is_(True),
            )
            .values(is_default=False)
        )
        await self.db.execute(stmt)

    @staticmethod
    def to_response(model: LLMModel) -> LLMModelResponse:
        """Convert LLM model to response schema with masked API key."""
        # Decrypt and mask the API key for display
        try:
            api_key = decrypt_api_key(model.api_key_encrypted)
            masked_key = mask_api_key(api_key)
        except Exception:
            masked_key = "***"

        return LLMModelResponse(
            id=model.id,
            name=model.name,
            provider=model.provider,
            model_id=model.model_id,
            base_url=model.base_url,
            api_key_masked=masked_key,
            max_tokens=model.max_tokens,
            temperature=model.temperature,
            top_p=model.top_p,
            is_enabled=model.is_enabled,
            is_default=model.is_default,
            description=model.description,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
