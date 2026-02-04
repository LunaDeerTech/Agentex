"""LLM Model configuration model."""

import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class LLMProvider(str, Enum):
    """Supported LLM providers."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class LLMModel(Base):
    """LLM Model configuration for AI providers."""

    __tablename__ = "llm_models"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    # Owner (who created this model config)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
        comment="Owner user ID",
    )

    # Model identification
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Display name for the model configuration",
    )
    provider: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="LLM provider (openai, anthropic)",
    )
    model_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Model identifier (e.g., gpt-4o, claude-3-opus)",
    )

    # Connection settings
    base_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="Custom API base URL (for Azure, local deployments)",
    )
    api_key_encrypted: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Encrypted API key",
    )

    # Model parameters
    max_tokens: Mapped[int] = mapped_column(
        Integer,
        default=4096,
        nullable=False,
        comment="Maximum tokens for responses",
    )
    temperature: Mapped[float] = mapped_column(
        Float,
        default=0.7,
        nullable=False,
        comment="Temperature parameter (0.0-2.0)",
    )
    top_p: Mapped[float] = mapped_column(
        Float,
        default=1.0,
        nullable=False,
        comment="Top-p (nucleus) sampling parameter",
    )

    # Configuration
    is_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Whether this model config is enabled",
    )
    is_default: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether this is the default model for the user",
    )

    # Metadata
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Optional description",
    )

    # Soft delete
    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
        comment="Soft delete flag",
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Deletion timestamp",
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return (
            f"<LLMModel(id={self.id}, name='{self.name}', provider='{self.provider}')>"
        )
