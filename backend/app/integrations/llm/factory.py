"""LLM client factory for creating provider-specific clients."""

from typing import Type

from app.integrations.llm.anthropic import AnthropicClient
from app.integrations.llm.base import BaseLLMClient, LLMConfig
from app.integrations.llm.openai import OpenAIClient


class LLMClientFactory:
    """Factory for creating LLM clients based on provider."""

    _providers: dict[str, Type[BaseLLMClient]] = {
        "openai": OpenAIClient,
        "anthropic": AnthropicClient,
    }

    @classmethod
    def register(cls, provider: str, client_class: Type[BaseLLMClient]) -> None:
        """
        Register a new provider client.

        Args:
            provider: Provider name
            client_class: Client class that extends BaseLLMClient
        """
        cls._providers[provider.lower()] = client_class

    @classmethod
    def create(cls, provider: str, config: LLMConfig) -> BaseLLMClient:
        """
        Create an LLM client for the specified provider.

        Args:
            provider: Provider name (openai, anthropic)
            config: LLM configuration

        Returns:
            Configured LLM client instance

        Raises:
            ValueError: If provider is not supported
        """
        provider_lower = provider.lower()
        if provider_lower not in cls._providers:
            raise ValueError(
                f"Unsupported LLM provider: {provider}. "
                f"Supported providers: {list(cls._providers.keys())}"
            )

        client_class = cls._providers[provider_lower]
        return client_class(config)

    @classmethod
    def list_providers(cls) -> list[str]:
        """Return list of supported providers."""
        return list(cls._providers.keys())


def get_llm_client(
    provider: str,
    model_id: str,
    api_key: str,
    base_url: str | None = None,
    max_tokens: int = 4096,
    temperature: float = 0.7,
    top_p: float = 1.0,
    timeout: int = 60,
) -> BaseLLMClient:
    """
    Convenience function to create an LLM client.

    Args:
        provider: Provider name (openai, anthropic)
        model_id: Model identifier
        api_key: API key
        base_url: Custom base URL (optional)
        max_tokens: Maximum tokens (default: 4096)
        temperature: Temperature parameter (default: 0.7)
        top_p: Top-p parameter (default: 1.0)
        timeout: Request timeout in seconds (default: 60)

    Returns:
        Configured LLM client instance
    """
    config = LLMConfig(
        model_id=model_id,
        api_key=api_key,
        base_url=base_url,
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
        timeout=timeout,
    )
    return LLMClientFactory.create(provider, config)
