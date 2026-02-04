"""Base LLM client abstract class."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, AsyncGenerator, Optional


class MessageRole(str, Enum):
    """Role of a message in a conversation."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


@dataclass
class LLMMessage:
    """Represents a message in a conversation."""

    role: MessageRole
    content: str
    name: Optional[str] = None
    tool_call_id: Optional[str] = None
    tool_calls: Optional[list[dict]] = None


@dataclass
class LLMResponse:
    """Response from an LLM."""

    content: str
    role: MessageRole = MessageRole.ASSISTANT
    finish_reason: Optional[str] = None
    tool_calls: Optional[list[dict]] = None
    usage: Optional[dict] = None
    model: Optional[str] = None
    raw_response: Optional[dict] = None


@dataclass
class LLMStreamChunk:
    """A chunk of streamed response from an LLM."""

    content: str
    finish_reason: Optional[str] = None
    tool_calls: Optional[list[dict]] = None
    is_final: bool = False


@dataclass
class LLMConfig:
    """Configuration for LLM client."""

    model_id: str
    api_key: str
    base_url: Optional[str] = None
    max_tokens: int = 4096
    temperature: float = 0.7
    top_p: float = 1.0
    timeout: int = 60
    extra_params: dict = field(default_factory=dict)


class BaseLLMClient(ABC):
    """Abstract base class for LLM clients."""

    def __init__(self, config: LLMConfig):
        """
        Initialize the LLM client.

        Args:
            config: LLM configuration object
        """
        self.config = config

    @property
    @abstractmethod
    def provider(self) -> str:
        """Return the provider name."""
        pass

    @abstractmethod
    async def chat(
        self,
        messages: list[LLMMessage],
        tools: Optional[list[dict]] = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """
        Send a chat completion request.

        Args:
            messages: List of messages in the conversation
            tools: Optional list of tool definitions
            **kwargs: Additional provider-specific parameters

        Returns:
            LLMResponse with the model's response
        """
        pass

    @abstractmethod
    async def chat_stream(
        self,
        messages: list[LLMMessage],
        tools: Optional[list[dict]] = None,
        **kwargs: Any,
    ) -> AsyncGenerator[LLMStreamChunk, None]:
        """
        Send a streaming chat completion request.

        Args:
            messages: List of messages in the conversation
            tools: Optional list of tool definitions
            **kwargs: Additional provider-specific parameters

        Yields:
            LLMStreamChunk objects as they arrive
        """
        pass

    @abstractmethod
    async def test_connection(self) -> tuple[bool, str, Optional[dict]]:
        """
        Test the connection to the LLM provider.

        Returns:
            Tuple of (success, message, optional model info)
        """
        pass

    def _merge_config(self, **kwargs: Any) -> dict:
        """Merge default config with request-specific overrides."""
        return {
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "temperature": kwargs.get("temperature", self.config.temperature),
            "top_p": kwargs.get("top_p", self.config.top_p),
            **self.config.extra_params,
            **{
                k: v
                for k, v in kwargs.items()
                if k not in ["max_tokens", "temperature", "top_p"]
            },
        }
