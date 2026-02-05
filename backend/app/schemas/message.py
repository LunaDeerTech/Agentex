"""
Message-related Pydantic schemas.
"""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class MessageCreateSchema(BaseModel):
    """Schema for creating a new message."""

    role: str = Field(..., pattern="^(user|assistant|system|tool)$")
    content: str = Field(..., min_length=1)
    meta: Optional[dict[str, Any]] = Field(default_factory=dict)

    class Config:
        json_schema_extra = {
            "example": {
                "role": "user",
                "content": "Hello, how can you help me?",
                "meta": {},
            }
        }


class MessageSchema(BaseModel):
    """Schema for message response."""

    id: UUID
    session_id: UUID
    role: str
    content: str
    meta: dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "session_id": "123e4567-e89b-12d3-a456-426614174001",
                "role": "user",
                "content": "Hello, how can you help me?",
                "meta": {},
                "created_at": "2026-02-05T10:00:00Z",
            }
        }


class MessageListSchema(BaseModel):
    """Schema for paginated message list response."""

    items: list[MessageSchema]
    total: int
    page: int
    page_size: int

    class Config:
        json_schema_extra = {
            "example": {"items": [], "total": 50, "page": 1, "page_size": 20}
        }
