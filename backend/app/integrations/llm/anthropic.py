"""Anthropic LLM client implementation."""

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


class AnthropicClient(BaseLLMClient):
    """Anthropic API client supporting Claude models."""

    DEFAULT_BASE_URL = "https://api.anthropic.com"
    ANTHROPIC_VERSION = "2023-06-01"

    def __init__(self, config: LLMConfig):
        """Initialize Anthropic client."""
        super().__init__(config)
        self.base_url = (config.base_url or self.DEFAULT_BASE_URL).rstrip("/")

    @property
    def provider(self) -> str:
        return "anthropic"

    def _get_headers(self) -> dict[str, str]:
        """Get headers for API requests."""
        return {
            "x-api-key": self.config.api_key,
            "anthropic-version": self.ANTHROPIC_VERSION,
            "Content-Type": "application/json",
        }

    def _format_messages(
        self, messages: list[LLMMessage]
    ) -> tuple[Optional[str], list[dict]]:
        """
        Convert LLMMessage objects to Anthropic format.

        Anthropic requires system message to be separate from messages array.

        Returns:
            Tuple of (system_prompt, messages_list)
        """
        system_prompt = None
        formatted = []

        for msg in messages or []:
            if msg.role == MessageRole.SYSTEM:
                system_prompt = msg.content
                continue

            # Anthropic uses "user" and "assistant" roles
            role = msg.role.value
            if role == "tool":
                # Tool results go as user messages with tool_result content
                formatted.append(
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": msg.tool_call_id,
                                "content": msg.content,
                            }
                        ],
                    }
                )
            else:
                content: Any = msg.content
                # If there are tool calls, format them properly
                if msg.tool_calls:
                    content = []
                    if msg.content:
                        content.append({"type": "text", "text": msg.content})
                    for tc in msg.tool_calls:
                        content.append(
                            {
                                "type": "tool_use",
                                "id": tc["id"],
                                "name": tc["function"]["name"],
                                "input": (
                                    json.loads(tc["function"]["arguments"])
                                    if isinstance(tc["function"]["arguments"], str)
                                    else tc["function"]["arguments"]
                                ),
                            }
                        )

                formatted.append(
                    {
                        "role": role,
                        "content": content,
                    }
                )

        return system_prompt, formatted

    def _format_tools(self, tools: Optional[list[dict]]) -> Optional[list[dict]]:
        """Format tools for Anthropic API."""
        if not tools:
            return None
        return [
            {
                "name": tool["name"],
                "description": tool.get("description", ""),
                "input_schema": tool.get(
                    "parameters", {"type": "object", "properties": {}}
                ),
            }
            for tool in tools
        ]

    def _parse_response_content(
        self, content_blocks: list[dict]
    ) -> tuple[str, Optional[list[dict]]]:
        """Parse Anthropic content blocks into text and tool calls."""
        text_parts = []
        tool_calls = []

        for block in content_blocks:
            if block["type"] == "text":
                text_parts.append(block["text"])
            elif block["type"] == "tool_use":
                tool_calls.append(
                    {
                        "id": block["id"],
                        "type": "function",
                        "function": {
                            "name": block["name"],
                            "arguments": (
                                json.dumps(block["input"])
                                if isinstance(block["input"], dict)
                                else block["input"]
                            ),
                        },
                    }
                )

        return "".join(text_parts), tool_calls if tool_calls else None

    async def chat(
        self,
        messages: list[LLMMessage],
        tools: Optional[list[dict]] = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Send a chat completion request to Anthropic."""
        config = self._merge_config(**kwargs)

        system_prompt, formatted_messages = self._format_messages(messages)

        payload: dict[str, Any] = {
            "model": self.config.model_id,
            "messages": formatted_messages,
            "max_tokens": config["max_tokens"],
            "temperature": config["temperature"],
            "top_p": config["top_p"],
        }

        if system_prompt:
            payload["system"] = system_prompt

        formatted_tools = self._format_tools(tools)
        if formatted_tools:
            payload["tools"] = formatted_tools

        async with httpx.AsyncClient(timeout=self.config.timeout) as client:
            response = await client.post(
                f"{self.base_url}/v1/messages",
                headers=self._get_headers(),
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

        content, tool_calls = self._parse_response_content(data["content"])

        return LLMResponse(
            content=content,
            role=MessageRole.ASSISTANT,
            finish_reason=data.get("stop_reason"),
            tool_calls=tool_calls,
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
        """Send a streaming chat completion request to Anthropic."""
        config = self._merge_config(**kwargs)

        system_prompt, formatted_messages = self._format_messages(messages)

        payload: dict[str, Any] = {
            "model": self.config.model_id,
            "messages": formatted_messages,
            "max_tokens": config["max_tokens"],
            "temperature": config["temperature"],
            "top_p": config["top_p"],
            "stream": True,
        }

        if system_prompt:
            payload["system"] = system_prompt

        formatted_tools = self._format_tools(tools)
        if formatted_tools:
            payload["tools"] = formatted_tools

        async with httpx.AsyncClient(timeout=self.config.timeout) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/v1/messages",
                headers=self._get_headers(),
                json=payload,
            ) as response:
                response.raise_for_status()

                current_tool_use: Optional[dict] = None
                tool_calls_list: list[dict] = []

                async for line in response.aiter_lines():
                    if not line.startswith("data: "):
                        continue

                    data_str = line[6:]
                    if not data_str:
                        continue

                    try:
                        data = json.loads(data_str)
                        event_type = data.get("type")

                        if event_type == "content_block_start":
                            block = data.get("content_block", {})
                            if block.get("type") == "tool_use":
                                current_tool_use = {
                                    "id": block["id"],
                                    "type": "function",
                                    "function": {
                                        "name": block["name"],
                                        "arguments": "",
                                    },
                                }

                        elif event_type == "content_block_delta":
                            delta = data.get("delta", {})

                            if delta.get("type") == "text_delta":
                                yield LLMStreamChunk(
                                    content=delta.get("text", ""),
                                    is_final=False,
                                )

                            elif (
                                delta.get("type") == "input_json_delta"
                                and current_tool_use
                            ):
                                current_tool_use["function"]["arguments"] += delta.get(
                                    "partial_json", ""
                                )

                        elif event_type == "content_block_stop":
                            if current_tool_use:
                                tool_calls_list.append(current_tool_use)
                                current_tool_use = None

                        elif event_type == "message_delta":
                            delta = data.get("delta", {})
                            stop_reason = delta.get("stop_reason")
                            if stop_reason:
                                yield LLMStreamChunk(
                                    content="",
                                    finish_reason=stop_reason,
                                    tool_calls=(
                                        tool_calls_list if tool_calls_list else None
                                    ),
                                    is_final=True,
                                )

                        elif event_type == "message_stop":
                            yield LLMStreamChunk(
                                content="",
                                is_final=True,
                            )

                    except json.JSONDecodeError:
                        continue

    async def test_connection(self) -> tuple[bool, str, Optional[dict]]:
        """Test connection to Anthropic API."""
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
