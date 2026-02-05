"""
Agent module for Agentex.

This module contains the Agent architecture implementations including:
- BaseAgent: Abstract base class for all agents
- ReActAgent: Reasoning and Acting agent implementation
- AgenticRAGAgent: Retrieval-Augmented Generation agent
- PlanAndExecuteAgent: Plan and Execute agent for complex tasks
- AgentFactory: Factory for creating agent instances
"""

from app.agents.agentic_rag import AgenticRAGAgent
from app.agents.base import BaseAgent
from app.agents.events import (
    AgentEvent,
    EventType,
    RunErrorEvent,
    RunFinishedEvent,
    RunStartedEvent,
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
from app.agents.factory import AgentFactory, create_agent
from app.agents.plan_execute import PlanAndExecuteAgent
from app.agents.react import ReActAgent

__all__ = [
    # Base
    "BaseAgent",
    # Events
    "AgentEvent",
    "EventType",
    "RunStartedEvent",
    "RunFinishedEvent",
    "RunErrorEvent",
    "TextMessageStartEvent",
    "TextMessageContentEvent",
    "TextMessageEndEvent",
    "ToolCallStartEvent",
    "ToolCallArgsEvent",
    "ToolCallEndEvent",
    "ToolCallResultEvent",
    "StepStartedEvent",
    "StepFinishedEvent",
    # Factory
    "AgentFactory",
    "create_agent",
    # Agents
    "ReActAgent",
    "AgenticRAGAgent",
    "PlanAndExecuteAgent",
]
