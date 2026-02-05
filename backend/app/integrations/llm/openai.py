"""OpenAI LLM client implementation."""

import json
import time
from typing import Any, AsyncGenerator, Optional

import httpx

from app.integrations.llm.base import (
    BaseLLMClient,
    LLMConfig,
    LLMMessage,
    LLMResponse,
    LLMStreamChunk,
    MessageRole,
)


class OpenAIClient(BaseLLMClient):
    """OpenAI API client supporting GPT models."""

    DEFAULT_BASE_URL = "https://api.openai.com/v1"

    def __init__(self, config: LLMConfig):
        """Initialize OpenAI client."""
        super().__init__(config)
        self.base_url = (config.base_url or self.DEFAULT_BASE_URL).rstrip("/")

    @property
    def provider(self) -> str:
        return "openai"

    def _get_headers(self) -> dict[str, str]:
        """Get headers for API requests."""
        return {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        }

    def _format_messages(self, messages: list[LLMMessage]) -> list[dict]:
        """Convert LLMMessage objects to OpenAI format."""
        formatted = []
        for msg in messages or []:
            message_dict: dict[str, Any] = {
                "role": msg.role.value,
                "content": msg.content or "",
            }
            if msg.name:
                message_dict["name"] = msg.name
            if msg.tool_call_id:
                message_dict["tool_call_id"] = msg.tool_call_id
            if msg.tool_calls:
                message_dict["tool_calls"] = msg.tool_calls
            formatted.append(message_dict)
        return formatted

    def _format_tools(self, tools: Optional[list[dict]]) -> Optional[list[dict]]:
        """Format tools for OpenAI API."""
        if not tools:
            return None
        return [
            {
                "type": "function",
                "function": tool,
            }
            for tool in tools
        ]

    async def chat(
        self,
        messages: list[LLMMessage],
        tools: Optional[list[dict]] = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Send a chat completion request to OpenAI."""
        config = self._merge_config(**kwargs)

        payload: dict[str, Any] = {
            "model": self.config.model_id,
            "messages": self._format_messages(messages),
            "max_tokens": config["max_tokens"],
            "temperature": config["temperature"],
            "top_p": config["top_p"],
        }

        formatted_tools = self._format_tools(tools)
        if formatted_tools:
            payload["tools"] = formatted_tools
            payload["tool_choice"] = kwargs.get("tool_choice", "auto")

        async with httpx.AsyncClient(timeout=self.config.timeout) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=self._get_headers(),
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

        choice = data["choices"][0]
        message = choice["message"]

        return LLMResponse(
            content=message.get("content") or "",
            role=MessageRole.ASSISTANT,
            finish_reason=choice.get("finish_reason"),
            tool_calls=message.get("tool_calls"),
            usage=data.get("usage"),
            model=data.get("model"),
            raw_response=data,
        )

    async def chat_stream(
        self,
        messages: list[LLMMessage],
        tools: Optional[list[dict]] = None,
        **kwargs: Any,
    ) -> AsyncGenerator[LLMStreamChunk, None]:
        """Send a streaming chat completion request to OpenAI."""
        config = self._merge_config(**kwargs)

        payload: dict[str, Any] = {
            "model": self.config.model_id,
            "messages": self._format_messages(messages),
            "max_tokens": config["max_tokens"],
            "temperature": config["temperature"],
            "top_p": config["top_p"],
            "stream": True,
        }

        formatted_tools = self._format_tools(tools)
        if formatted_tools:
            payload["tools"] = formatted_tools
            payload["tool_choice"] = kwargs.get("tool_choice", "auto")

        async with httpx.AsyncClient(timeout=self.config.timeout) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                headers=self._get_headers(),
                json=payload,
            ) as response:
                response.raise_for_status()

                tool_calls_buffer: dict[int, dict] = {}

                async for line in response.aiter_lines():
                    if not line.startswith("data: "):
                        continue

                    data_str = line[6:]  # Remove "data: " prefix
                    if data_str == "[DONE]":
                        yield LLMStreamChunk(
                            content="",
                            is_final=True,
                        )
                        break

                    try:
                        data = json.loads(data_str)

                        # Check if choices array is not empty
                        if not data.get("choices"):
                            continue

                        choice = data["choices"][0]
                        delta = choice.get("delta", {})

                        content = delta.get("content", "")
                        finish_reason = choice.get("finish_reason")

                        # Handle tool calls in streaming
                        tool_calls = None
                        if delta.get("tool_calls"):
                            for tc in delta["tool_calls"]:
                                idx = tc["index"]
                                if idx not in tool_calls_buffer:
                                    tool_calls_buffer[idx] = {
                                        "id": tc.get("id", ""),
                                        "type": "function",
                                        "function": {
                                            "name": "",
                                            "arguments": "",
                                        },
                                    }
                                if "id" in tc:
                                    tool_calls_buffer[idx]["id"] = tc["id"]
                                if "function" in tc:
                                    if "name" in tc["function"]:
                                        tool_calls_buffer[idx]["function"]["name"] = tc[
                                            "function"
                                        ]["name"]
                                    if "arguments" in tc["function"]:
                                        tool_calls_buffer[idx]["function"][
                                            "arguments"
                                        ] += tc["function"]["arguments"]

                        if finish_reason == "tool_calls" and tool_calls_buffer:
                            tool_calls = list(tool_calls_buffer.values())

                        yield LLMStreamChunk(
                            content=content,
                            finish_reason=finish_reason,
                            tool_calls=tool_calls,
                            is_final=finish_reason is not None,
                        )

                    except json.JSONDecodeError:
                        continue

    async def test_connection(self) -> tuple[bool, str, Optional[dict]]:
        """Test connection to OpenAI API."""
        start_time = time.time()

        try:
            test_messages = [
                LLMMessage(
                    role=MessageRole.USER,
                    content="Say 'OK' to confirm the connection works.",
                )
            ]

            response = await self.chat(
                messages=test_messages,
                max_tokens=10,
                temperature=0,
            )

            latency_ms = int((time.time() - start_time) * 1000)

            return (
                True,
                f"Connection successful. Model: {response.model}",
                {
                    "model": response.model,
                    "latency_ms": latency_ms,
                    "response": response.content[:100],
                },
            )

        except httpx.HTTPStatusError as e:
            error_body = e.response.text
            return (
                False,
                f"HTTP {e.response.status_code}: {error_body[:200]}",
                None,
            )
        except httpx.RequestError as e:
            return (
                False,
                f"Connection error: {str(e)}",
                None,
            )
        except Exception as e:
            return (
                False,
                f"Unexpected error: {str(e)}",
                None,
            )
