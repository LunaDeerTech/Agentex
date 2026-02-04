"""User and API key schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserUpdateRequest(BaseModel):
    """User profile update request schema."""

    username: str | None = Field(
        default=None, min_length=3, max_length=50, pattern="^[a-zA-Z0-9_-]+$"
    )
    email: EmailStr | None = None
    avatar_url: str | None = Field(default=None, max_length=500)


class UserPasswordUpdateRequest(BaseModel):
    """User password update request schema."""

    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8, max_length=100)

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class ApiKeyCreateRequest(BaseModel):
    """API key creation request."""

    name: str = Field(..., min_length=1, max_length=100)
    expires_at: datetime | None = None


class ApiKeyResponse(BaseModel):
    """API key response schema."""

    id: UUID
    name: str
    key_prefix: str
    last_used_at: datetime | None = None
    expires_at: datetime | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class ApiKeyCreateResponse(BaseModel):
    """API key creation response with the raw key (shown once)."""

    api_key: str
    key: ApiKeyResponse


class OperationStatus(BaseModel):
    """Generic operation result schema."""

    message: str
