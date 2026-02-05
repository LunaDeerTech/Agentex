"""
Base Agent abstract class.

This module defines the abstract base class for all Agent implementations
in the Agentex platform. It provides the common interface and shared
functionality for agents.
"""

import asyncio
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator, Callable
from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

from app.agents.events import (
    AgentEvent,
    RunErrorEvent,
    RunFinishedEvent,
    RunStartedEvent,
    StepContentEvent,
    StepFinishedEvent,
    StepStartedEvent,
    TextMessageContentEvent,
    TextMessageEndEvent,
    TextMessageStartEvent,
    ToolCallArgsEvent,
    ToolCallEndEvent,
    ToolCallResultEvent,
    ToolCallStartEvent,
)
from app.integrations.llm.base import BaseLLMClient, LLMMessage


@dataclass
class Tool:
    """Represents a tool that can be called by the agent."""

    name: str
    description: str
    parameters: dict[str, Any] = field(default_factory=dict)
    handler: Callable[..., Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert tool to dictionary format for LLM."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
        }


@dataclass
class ToolResult:
    """Result of a tool execution."""

    tool_call_id: str
    tool_name: str
    content: str
    success: bool = True
    error: str | None = None


@dataclass
class AgentConfig:
    """Configuration for an agent."""

    max_iterations: int = 10
    temperature: float = 0.7
    max_tokens: int = 4096
    system_prompt: str | None = None
    timeout: int = 300  # seconds


@dataclass
class AgentContext:
    """Runtime context for agent execution."""

    thread_id: str = ""
    run_id: str = field(default_factory=lambda: str(uuid4()))
    message_history: list[LLMMessage] = field(default_factory=list)
    state: dict[str, Any] = field(default_factory=dict)
    cancelled: bool = False

    def cancel(self) -> None:
        """Cancel the current run."""
        self.cancelled = True

    def is_cancelled(self) -> bool:
        """Check if the run is cancelled."""
        return self.cancelled


class BaseAgent(ABC):
    """
    Abstract base class for all Agent implementations.

    Agents process user messages and produce a stream of AG-UI events
    that represent the agent's thinking process, tool calls, and responses.

    Attributes:
        llm_client: The LLM client for generating responses
        tools: List of available tools
        config: Agent configuration
    """

    def __init__(
        self,
        llm_client: BaseLLMClient,
        tools: list[Tool] | None = None,
        config: AgentConfig | None = None,
    ):
        """
        Initialize the agent.

        Args:
            llm_client: LLM client for model calls
            tools: Optional list of tools available to the agent
            config: Optional agent configuration
        """
        self.llm_client = llm_client
        self.tools = tools or []
        self.config = config or AgentConfig()
        self._tool_handlers: dict[str, Callable[..., Any]] = {}

        # Register tool handlers
        for tool in self.tools or []:
            if tool.handler:
                self._tool_handlers[tool.name] = tool.handler

    @property
    @abstractmethod
    def agent_type(self) -> str:
        """Return the agent type identifier."""
        pass

    async def run(
        self,
        message: str,
        context: AgentContext | None = None,
    ) -> AsyncIterator[AgentEvent]:
        """
        Run the agent with the given message.

        This is the main entry point for agent execution. It handles the
        lifecycle events and delegates to the internal processing method.

        Args:
            message: The user message to process
            context: Optional execution context

        Yields:
            AgentEvent objects representing the agent's activity
        """
        # Create context if not provided
        if context is None:
            context = AgentContext(
                thread_id=str(uuid4()),
                run_id=str(uuid4()),
            )

        # Emit run started
        yield RunStartedEvent(
            thread_id=context.thread_id,
            run_id=context.run_id,
        )

        try:
            # Process the message
            async for event in self._process(message, context):
                if context.is_cancelled():
                    yield RunErrorEvent(
                        message="Run cancelled by user",
                        code="RUN_CANCELLED",
                    )
                    return
                yield event

            # Emit run finished
            yield RunFinishedEvent(
                thread_id=context.thread_id,
                run_id=context.run_id,
                result={"status": "completed"},
            )

        except asyncio.CancelledError:
            yield RunErrorEvent(
                message="Run cancelled",
                code="RUN_CANCELLED",
            )
        except Exception as e:
            yield RunErrorEvent(
                message=str(e),
                code="AGENT_ERROR",
            )
            raise

    @abstractmethod
    async def _process(
        self,
        message: str,
        context: AgentContext,
    ) -> AsyncIterator[AgentEvent]:
        """
        Internal processing method to be implemented by subclasses.

        Args:
            message: The user message to process
            context: Execution context

        Yields:
            AgentEvent objects representing the agent's activity
        """
        # This is an abstract method - subclasses must implement
        # The yield statement makes this a proper async generator
        if False:  # pragma: no cover
            yield  # type: ignore[misc]

    # ============ Helper Methods ============

    def get_tools_for_llm(self) -> list[dict[str, Any]]:
        """Get tools in LLM-compatible format."""
        return [tool.to_dict() for tool in (self.tools or [])]

    async def call_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        tool_call_id: str | None = None,
    ) -> ToolResult:
        """
        Call a tool by name with given arguments.

        Args:
            tool_name: Name of the tool to call
            arguments: Arguments to pass to the tool
            tool_call_id: Optional ID for the tool call

        Returns:
            ToolResult with the execution result
        """
        tool_call_id = tool_call_id or str(uuid4())

        handler = self._tool_handlers.get(tool_name)
        if not handler:
            return ToolResult(
                tool_call_id=tool_call_id,
                tool_name=tool_name,
                content="",
                success=False,
                error=f"Tool '{tool_name}' not found",
            )

        try:
            # Call the tool handler
            if asyncio.iscoroutinefunction(handler):
                result = await handler(**arguments)
            else:
                result = handler(**arguments)

            # Convert result to string
            if isinstance(result, dict):
                import json

                content = json.dumps(result)
            else:
                content = str(result)

            return ToolResult(
                tool_call_id=tool_call_id,
                tool_name=tool_name,
                content=content,
                success=True,
            )

        except Exception as e:
            return ToolResult(
                tool_call_id=tool_call_id,
                tool_name=tool_name,
                content="",
                success=False,
                error=str(e),
            )

    def register_tool_handler(
        self,
        tool_name: str,
        handler: Callable[..., Any],
    ) -> None:
        """
        Register a handler for a tool.

        Args:
            tool_name: Name of the tool
            handler: Function to handle the tool call
        """
        self._tool_handlers[tool_name] = handler

    # ============ Event Helper Methods ============

    @staticmethod
    def emit_step_started(step_name: str) -> StepStartedEvent:
        """Create a step started event."""
        return StepStartedEvent(step_name=step_name)

    @staticmethod
    def emit_step_content(step_name: str, delta: str) -> StepContentEvent:
        """Create a step content event."""
        return StepContentEvent(step_name=step_name, delta=delta)

    @staticmethod
    def emit_step_finished(step_name: str) -> StepFinishedEvent:
        """Create a step finished event."""
        return StepFinishedEvent(step_name=step_name)

    @staticmethod
    def emit_text_start(
        message_id: str, role: str = "assistant"
    ) -> TextMessageStartEvent:
        """Create a text message start event."""
        return TextMessageStartEvent(message_id=message_id, role=role)

    @staticmethod
    def emit_text_content(message_id: str, delta: str) -> TextMessageContentEvent:
        """Create a text message content event."""
        return TextMessageContentEvent(message_id=message_id, delta=delta)

    @staticmethod
    def emit_text_end(message_id: str) -> TextMessageEndEvent:
        """Create a text message end event."""
        return TextMessageEndEvent(message_id=message_id)

    @staticmethod
    def emit_tool_call_start(
        tool_call_id: str,
        tool_name: str,
        parent_message_id: str | None = None,
    ) -> ToolCallStartEvent:
        """Create a tool call start event."""
        return ToolCallStartEvent(
            tool_call_id=tool_call_id,
            tool_call_name=tool_name,
            parent_message_id=parent_message_id,
        )

    @staticmethod
    def emit_tool_call_args(tool_call_id: str, delta: str) -> ToolCallArgsEvent:
        """Create a tool call args event."""
        return ToolCallArgsEvent(tool_call_id=tool_call_id, delta=delta)

    @staticmethod
    def emit_tool_call_end(tool_call_id: str) -> ToolCallEndEvent:
        """Create a tool call end event."""
        return ToolCallEndEvent(tool_call_id=tool_call_id)

    @staticmethod
    def emit_tool_call_result(
        tool_call_id: str,
        content: str,
        message_id: str | None = None,
    ) -> ToolCallResultEvent:
        """Create a tool call result event."""
        return ToolCallResultEvent(
            message_id=message_id or str(uuid4()),
            tool_call_id=tool_call_id,
            content=content,
        )
