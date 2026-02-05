"""
Session-related Pydantic schemas.
"""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class SessionSettingsSchema(BaseModel):
    """Session settings schema."""

    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=4096, ge=1, le=128000)
    system_prompt: Optional[str] = None
    knowledge_base_ids: Optional[list[UUID]] = Field(default_factory=list)
    mcp_connection_ids: Optional[list[UUID]] = Field(default_factory=list)
    skill_ids: Optional[list[UUID]] = Field(default_factory=list)

    class Config:
        json_schema_extra = {
            "example": {
                "temperature": 0.7,
                "max_tokens": 4096,
                "system_prompt": "You are a helpful assistant.",
                "knowledge_base_ids": [],
                "mcp_connection_ids": [],
                "skill_ids": [],
            }
        }


class SessionCreateSchema(BaseModel):
    """Schema for creating a new session."""

    title: Optional[str] = Field(None, max_length=200)
    agent_type: str = Field(
        default="react", pattern="^(react|agentic_rag|plan_execute)$"
    )
    model_config_id: Optional[UUID] = None
    settings: Optional[SessionSettingsSchema] = Field(
        default_factory=SessionSettingsSchema
    )

    @field_validator("agent_type")
    @classmethod
    def validate_agent_type(cls, v: str) -> str:
        allowed = {"react", "agentic_rag", "plan_execute"}
        if v not in allowed:
            raise ValueError(f"agent_type must be one of {allowed}")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "title": "My Chat Session",
                "agent_type": "react",
                "model_config_id": "123e4567-e89b-12d3-a456-426614174000",
                "settings": {"temperature": 0.7, "max_tokens": 4096},
            }
        }


class SessionUpdateSchema(BaseModel):
    """Schema for updating a session."""

    title: Optional[str] = Field(None, max_length=200)
    agent_type: Optional[str] = Field(
        None, pattern="^(react|agentic_rag|plan_execute)$"
    )
    model_config_id: Optional[UUID] = None
    settings: Optional[SessionSettingsSchema] = None

    @field_validator("agent_type")
    @classmethod
    def validate_agent_type(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            allowed = {"react", "agentic_rag", "plan_execute"}
            if v not in allowed:
                raise ValueError(f"agent_type must be one of {allowed}")
        return v


class SessionSchema(BaseModel):
    """Schema for session response."""

    id: UUID
    user_id: UUID
    title: Optional[str] = None
    agent_type: str
    model_config_id: Optional[UUID] = None
    settings: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "123e4567-e89b-12d3-a456-426614174001",
                "title": "My Chat Session",
                "agent_type": "react",
                "model_config_id": "123e4567-e89b-12d3-a456-426614174002",
                "settings": {"temperature": 0.7, "max_tokens": 4096},
                "created_at": "2026-02-05T10:00:00Z",
                "updated_at": "2026-02-05T10:00:00Z",
            }
        }


class SessionListSchema(BaseModel):
    """Schema for paginated session list response."""

    items: list[SessionSchema]
    total: int
    page: int
    page_size: int

    class Config:
        json_schema_extra = {
            "example": {"items": [], "total": 10, "page": 1, "page_size": 20}
        }
