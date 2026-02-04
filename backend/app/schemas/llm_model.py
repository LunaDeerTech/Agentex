"""LLM Model schemas for request/response validation."""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class LLMProviderEnum(str, Enum):
    """Supported LLM providers."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"


# ============== Request Schemas ==============


class LLMModelCreateRequest(BaseModel):
    """Request schema for creating a new LLM model configuration."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Display name for the model configuration",
    )
    provider: LLMProviderEnum = Field(
        ...,
        description="LLM provider (openai, anthropic)",
    )
    model_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Model identifier (e.g., gpt-4o, claude-3-opus-20240229)",
    )
    api_key: str = Field(
        ...,
        min_length=1,
        description="API key for the provider",
    )
    base_url: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Custom API base URL (for Azure, local deployments)",
    )
    max_tokens: int = Field(
        default=4096,
        ge=1,
        le=200000,
        description="Maximum tokens for responses",
    )
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Temperature parameter (0.0-2.0)",
    )
    top_p: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Top-p (nucleus) sampling parameter",
    )
    is_default: bool = Field(
        default=False,
        description="Set as default model for this user",
    )
    description: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Optional description",
    )

    @field_validator("base_url")
    @classmethod
    def validate_base_url(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v.strip():
            v = v.strip().rstrip("/")
            if not v.startswith(("http://", "https://")):
                raise ValueError("Base URL must start with http:// or https://")
        return v if v else None


class LLMModelUpdateRequest(BaseModel):
    """Request schema for updating an LLM model configuration."""

    name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=100,
    )
    model_id: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=100,
    )
    api_key: Optional[str] = Field(
        default=None,
        min_length=1,
        description="New API key (will be re-encrypted)",
    )
    base_url: Optional[str] = Field(
        default=None,
        max_length=500,
    )
    max_tokens: Optional[int] = Field(
        default=None,
        ge=1,
        le=200000,
    )
    temperature: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=2.0,
    )
    top_p: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )
    is_enabled: Optional[bool] = None
    is_default: Optional[bool] = None
    description: Optional[str] = Field(
        default=None,
        max_length=500,
    )

    @field_validator("base_url")
    @classmethod
    def validate_base_url(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v.strip():
            v = v.strip().rstrip("/")
            if not v.startswith(("http://", "https://")):
                raise ValueError("Base URL must start with http:// or https://")
        return v if v else None


class LLMModelTestRequest(BaseModel):
    """Request schema for testing an LLM model configuration."""

    prompt: str = Field(
        default="Hello! Please respond with 'OK' to confirm the connection works.",
        min_length=1,
        max_length=1000,
        description="Test prompt to send to the model",
    )


# ============== Response Schemas ==============


class LLMModelResponse(BaseModel):
    """Response schema for LLM model configuration (without sensitive data)."""

    id: UUID
    name: str
    provider: str
    model_id: str
    base_url: Optional[str] = None
    api_key_masked: str = Field(
        ...,
        description="Masked API key for display",
    )
    max_tokens: int
    temperature: float
    top_p: float
    is_enabled: bool
    is_default: bool
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LLMModelTestResponse(BaseModel):
    """Response schema for model test results."""

    success: bool
    message: str
    response_text: Optional[str] = None
    latency_ms: Optional[int] = None
    model_info: Optional[dict] = None


class LLMModelListResponse(BaseModel):
    """Response schema for listing LLM models."""

    models: list[LLMModelResponse]
    total: int


class OperationStatus(BaseModel):
    """Generic operation result schema."""

    message: str
