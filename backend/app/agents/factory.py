"""
Agent Factory for creating agent instances.

This module provides a factory pattern for creating different types of agents
based on configuration. It handles agent registration and instantiation.
"""

from typing import Any

from app.agents.agentic_rag import AgenticRAGAgent
from app.agents.base import AgentConfig, BaseAgent, Tool
from app.agents.plan_execute import PlanAndExecuteAgent
from app.agents.react import ReActAgent
from app.integrations.llm.base import BaseLLMClient


class AgentFactory:
    """
    Factory for creating agent instances.

    This factory maintains a registry of agent types and provides
    methods to create agent instances with proper configuration.
    """

    _agents: dict[str, type[BaseAgent]] = {
        "react": ReActAgent,
        "agentic_rag": AgenticRAGAgent,
        "plan_execute": PlanAndExecuteAgent,
    }

    @classmethod
    def register(cls, agent_type: str, agent_class: type[BaseAgent]) -> None:
        """
        Register a new agent type.

        Args:
            agent_type: The type identifier for the agent
            agent_class: The agent class to register
        """
        cls._agents[agent_type.lower()] = agent_class

    @classmethod
    def create(
        cls,
        agent_type: str,
        llm_client: BaseLLMClient,
        tools: list[Tool] | None = None,
        config: AgentConfig | None = None,
        **kwargs: Any,
    ) -> BaseAgent:
        """
        Create an agent instance.

        Args:
            agent_type: The type of agent to create
            llm_client: LLM client for the agent
            tools: Optional list of tools
            config: Optional agent configuration
            **kwargs: Additional arguments passed to the agent constructor

        Returns:
            Configured agent instance

        Raises:
            ValueError: If agent type is not supported
        """
        agent_type_lower = agent_type.lower()

        if agent_type_lower not in cls._agents:
            raise ValueError(
                f"Unsupported agent type: {agent_type}. "
                f"Supported types: {list(cls._agents.keys())}"
            )

        agent_class = cls._agents[agent_type_lower]
        return agent_class(
            llm_client=llm_client,
            tools=tools,
            config=config,
            **kwargs,
        )

    @classmethod
    def list_types(cls) -> list[str]:
        """Return list of supported agent types."""
        return list(cls._agents.keys())

    @classmethod
    def get_agent_info(cls, agent_type: str) -> dict[str, Any]:
        """
        Get information about an agent type.

        Args:
            agent_type: The type of agent

        Returns:
            Dictionary with agent information
        """
        agent_type_lower = agent_type.lower()

        if agent_type_lower not in cls._agents:
            raise ValueError(f"Unknown agent type: {agent_type}")

        agent_class = cls._agents[agent_type_lower]

        return {
            "type": agent_type_lower,
            "name": agent_class.__name__,
            "description": agent_class.__doc__ or "No description available",
        }


def create_agent(
    agent_type: str,
    llm_client: BaseLLMClient,
    tools: list[Tool] | None = None,
    config: AgentConfig | None = None,
    **kwargs: Any,
) -> BaseAgent:
    """
    Convenience function to create an agent.

    This is a shorthand for AgentFactory.create().

    Args:
        agent_type: The type of agent to create
        llm_client: LLM client for the agent
        tools: Optional list of tools
        config: Optional agent configuration
        **kwargs: Additional arguments passed to the agent constructor

    Returns:
        Configured agent instance
    """
    return AgentFactory.create(
        agent_type=agent_type,
        llm_client=llm_client,
        tools=tools,
        config=config,
        **kwargs,
    )
