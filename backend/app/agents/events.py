"""
AG-UI Event Types for Agent communication.

This module defines the event types used for Agent-User Interaction Protocol (AG-UI).
Events are sent as Server-Sent Events (SSE) to the frontend for real-time updates.
"""

import json
import time
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any
from uuid import uuid4


class EventType(str, Enum):
    """AG-UI Event types for agent communication."""

    # Lifecycle events
    RUN_STARTED = "RUN_STARTED"
    RUN_FINISHED = "RUN_FINISHED"
    RUN_ERROR = "RUN_ERROR"

    # Text message events
    TEXT_MESSAGE_START = "TEXT_MESSAGE_START"
    TEXT_MESSAGE_CONTENT = "TEXT_MESSAGE_CONTENT"
    TEXT_MESSAGE_END = "TEXT_MESSAGE_END"

    # Tool call events
    TOOL_CALL_START = "TOOL_CALL_START"
    TOOL_CALL_ARGS = "TOOL_CALL_ARGS"
    TOOL_CALL_END = "TOOL_CALL_END"
    TOOL_CALL_RESULT = "TOOL_CALL_RESULT"

    # Step events (for thinking process)
    STEP_STARTED = "STEP_STARTED"
    STEP_CONTENT = "STEP_CONTENT"
    STEP_FINISHED = "STEP_FINISHED"

    # State events
    STATE_SNAPSHOT = "STATE_SNAPSHOT"
    STATE_DELTA = "STATE_DELTA"


@dataclass
class AgentEvent:
    """Base class for all AG-UI events."""

    type: EventType
    timestamp: int = field(default_factory=lambda: int(time.time() * 1000))

    def to_dict(self) -> dict[str, Any]:
        """Convert event to dictionary."""
        data = asdict(self)
        data["type"] = self.type.value
        return data

    def to_sse(self) -> str:
        """Convert event to SSE format string."""
        data = self.to_dict()
        return f"event: {self.type.value}\ndata: {json.dumps(data)}\n\n"


# ============ Lifecycle Events ============


@dataclass
class RunStartedEvent(AgentEvent):
    """Event emitted when agent run starts."""

    type: EventType = field(default=EventType.RUN_STARTED)
    thread_id: str = ""
    run_id: str = ""


@dataclass
class RunFinishedEvent(AgentEvent):
    """Event emitted when agent run finishes successfully."""

    type: EventType = field(default=EventType.RUN_FINISHED)
    thread_id: str = ""
    run_id: str = ""
    result: dict[str, Any] | None = None


@dataclass
class RunErrorEvent(AgentEvent):
    """Event emitted when agent run encounters an error."""

    type: EventType = field(default=EventType.RUN_ERROR)
    message: str = ""
    code: str = "AGENT_ERROR"


# ============ Text Message Events ============


@dataclass
class TextMessageStartEvent(AgentEvent):
    """Event emitted when a text message starts."""

    type: EventType = field(default=EventType.TEXT_MESSAGE_START)
    message_id: str = field(default_factory=lambda: str(uuid4()))
    role: str = "assistant"


@dataclass
class TextMessageContentEvent(AgentEvent):
    """Event emitted for text message content (streaming)."""

    type: EventType = field(default=EventType.TEXT_MESSAGE_CONTENT)
    message_id: str = ""
    delta: str = ""


@dataclass
class TextMessageEndEvent(AgentEvent):
    """Event emitted when a text message ends."""

    type: EventType = field(default=EventType.TEXT_MESSAGE_END)
    message_id: str = ""


# ============ Tool Call Events ============


@dataclass
class ToolCallStartEvent(AgentEvent):
    """Event emitted when a tool call starts."""

    type: EventType = field(default=EventType.TOOL_CALL_START)
    tool_call_id: str = field(default_factory=lambda: str(uuid4()))
    tool_call_name: str = ""
    parent_message_id: str | None = None


@dataclass
class ToolCallArgsEvent(AgentEvent):
    """Event emitted for tool call arguments (streaming)."""

    type: EventType = field(default=EventType.TOOL_CALL_ARGS)
    tool_call_id: str = ""
    delta: str = ""


@dataclass
class ToolCallEndEvent(AgentEvent):
    """Event emitted when tool call arguments are complete."""

    type: EventType = field(default=EventType.TOOL_CALL_END)
    tool_call_id: str = ""


@dataclass
class ToolCallResultEvent(AgentEvent):
    """Event emitted when tool execution result is available."""

    type: EventType = field(default=EventType.TOOL_CALL_RESULT)
    message_id: str = field(default_factory=lambda: str(uuid4()))
    tool_call_id: str = ""
    content: str = ""
    role: str = "tool"


# ============ Step Events ============


@dataclass
class StepStartedEvent(AgentEvent):
    """Event emitted when a step (thinking process) starts."""

    type: EventType = field(default=EventType.STEP_STARTED)
    step_name: str = ""


@dataclass
class StepContentEvent(AgentEvent):
    """Event emitted for step content (streaming)."""

    type: EventType = field(default=EventType.STEP_CONTENT)
    step_name: str = ""
    delta: str = ""


@dataclass
class StepFinishedEvent(AgentEvent):
    """Event emitted when a step (thinking process) finishes."""

    type: EventType = field(default=EventType.STEP_FINISHED)
    step_name: str = ""


# ============ State Events ============


@dataclass
class StateSnapshotEvent(AgentEvent):
    """Event emitted for complete state snapshot."""

    type: EventType = field(default=EventType.STATE_SNAPSHOT)
    snapshot: dict[str, Any] = field(default_factory=dict)


@dataclass
class StateDeltaEvent(AgentEvent):
    """Event emitted for incremental state update (JSON Patch)."""

    type: EventType = field(default=EventType.STATE_DELTA)
    delta: list[dict[str, Any]] = field(default_factory=list)
