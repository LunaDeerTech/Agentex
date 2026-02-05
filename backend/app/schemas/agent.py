"""
Agent schemas for request/response validation.
"""

from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class ToolSchema(BaseModel):
    """Schema for tool definition."""

    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    parameters: dict[str, Any] = Field(
        default_factory=dict, description="JSON Schema for parameters"
    )


class MessageSchema(BaseModel):
    """Schema for a message in the conversation."""

    id: str = Field(..., description="Message ID")
    role: str = Field(
        ..., pattern="^(user|assistant|system|tool)$", description="Message role"
    )
    content: str = Field(..., description="Message content")
    name: str | None = Field(None, description="Name for tool messages")
    tool_call_id: str | None = Field(None, description="Tool call ID for tool results")


class ContextItemSchema(BaseModel):
    """Schema for context item."""

    description: str = Field(..., description="Context description")
    value: str = Field(..., description="Context value")


class ForwardedPropsSchema(BaseModel):
    """Schema for forwarded props (agent configuration)."""

    agent_type: str = Field(default="react", description="Agent type to use")
    model_id: UUID | None = Field(None, description="LLM model ID to use")
    knowledge_base_ids: list[UUID] = Field(
        default_factory=list, description="Knowledge base IDs"
    )
    mcp_connection_ids: list[UUID] = Field(
        default_factory=list, description="MCP connection IDs"
    )
    skill_ids: list[UUID] = Field(default_factory=list, description="SKILL IDs")
    temperature: float = Field(default=0.7, ge=0, le=2, description="Temperature")
    max_tokens: int = Field(default=4096, ge=1, le=128000, description="Max tokens")
    system_prompt: str | None = Field(None, description="System prompt override")


class RunAgentInput(BaseModel):
    """Input schema for running an agent (AG-UI protocol)."""

    thread_id: str = Field(..., description="Session/thread ID")
    run_id: str | None = Field(
        None, description="Run ID (auto-generated if not provided)"
    )
    state: dict[str, Any] = Field(default_factory=dict, description="Agent state")
    messages: list[MessageSchema] = Field(
        default_factory=list, description="Message history"
    )
    tools: list[ToolSchema] = Field(default_factory=list, description="Available tools")
    context: list[ContextItemSchema] = Field(
        default_factory=list, description="Context items"
    )
    forwarded_props: ForwardedPropsSchema = Field(
        default_factory=lambda: ForwardedPropsSchema(),
        description="Agent configuration",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "thread_id": "session-uuid",
                "messages": [
                    {"id": "msg-1", "role": "user", "content": "Hello, how are you?"}
                ],
                "tools": [],
                "forwarded_props": {"agent_type": "react", "temperature": 0.7},
            }
        }


class StopRunInput(BaseModel):
    """Input schema for stopping a run."""

    run_id: str = Field(..., description="Run ID to stop")


class StopRunResponse(BaseModel):
    """Response schema for stopping a run."""

    run_id: str
    stopped: bool


class AgentTypeInfo(BaseModel):
    """Information about an agent type."""

    type: str
    name: str
    description: str
    supports_tools: bool = True
    supports_knowledge_base: bool = True


class AgentTypesResponse(BaseModel):
    """Response schema for listing agent types."""

    items: list[AgentTypeInfo]
