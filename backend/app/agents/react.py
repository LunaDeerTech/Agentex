"""
ReAct Agent implementation.

ReAct (Reasoning and Acting) is an agent architecture that alternates between
reasoning about the current state and taking actions. It follows the pattern:
1. Thought: Analyze the situation and decide what to do
2. Action: Execute a tool call if needed
3. Observation: Process the result
4. Repeat until a final answer is reached

Reference: https://arxiv.org/abs/2210.03629
"""

import asyncio
import json
import re
from collections.abc import AsyncIterator
from typing import Any
from uuid import uuid4

from app.agents.base import AgentConfig, AgentContext, BaseAgent, Tool
from app.agents.events import AgentEvent
from app.integrations.llm.base import BaseLLMClient, LLMMessage, MessageRole

REACT_SYSTEM_PROMPT = """You are a helpful AI assistant that can use tools to help answer questions.

You have access to the following tools:
{tools_description}

When you need to use a tool, respond with the following JSON format:
```json
{{
    "thought": "Your reasoning about what to do",
    "action": "tool_name",
    "action_input": {{"param1": "value1"}}
}}
```

When you have the final answer and don't need any more tools, respond with:
```json
{{
    "thought": "Your final reasoning",
    "action": "final_answer",
    "action_input": {{"answer": "Your final answer to the user"}}
}}
```

Important rules:
1. Always think step by step before taking action
2. Only use one tool at a time
3. Wait for the observation before continuing
4. Provide clear, helpful answers
5. If you cannot answer with the available tools, explain what you need

Current conversation:
{history}
"""


class ReActAgent(BaseAgent):
    """
    ReAct Agent implementation.

    This agent uses a Thought-Action-Observation loop to process user
    requests. It can reason about problems and use tools to gather
    information before providing a final answer.
    """

    def __init__(
        self,
        llm_client: BaseLLMClient,
        tools: list[Tool] | None = None,
        config: AgentConfig | None = None,
        system_prompt: str | None = None,
    ):
        """
        Initialize the ReAct agent.

        Args:
            llm_client: LLM client for model calls
            tools: Optional list of tools available to the agent
            config: Optional agent configuration
            system_prompt: Optional custom system prompt
        """
        super().__init__(llm_client, tools, config)
        self._custom_system_prompt = system_prompt

    @property
    def agent_type(self) -> str:
        return "react"

    def _build_system_prompt(self, context: AgentContext) -> str:
        """Build the system prompt with tool descriptions and history."""
        if self._custom_system_prompt:
            base_prompt = self._custom_system_prompt
        else:
            base_prompt = REACT_SYSTEM_PROMPT

        # Build tools description
        if self.tools:
            tools_desc = "\n".join(
                [
                    f"- {tool.name}: {tool.description}\n  Parameters: {json.dumps(tool.parameters)}"
                    for tool in (self.tools or [])
                ]
            )
        else:
            tools_desc = "No tools available."

        # Build history summary
        history_lines = []
        for msg in context.message_history[-10:]:  # Last 10 messages
            role = msg.role.value.capitalize()
            content = (
                msg.content[:200] + "..." if len(msg.content) > 200 else msg.content
            )
            history_lines.append(f"{role}: {content}")

        history = "\n".join(history_lines) if history_lines else "No previous messages."

        return base_prompt.format(
            tools_description=tools_desc,
            history=history,
        )

    def _parse_response(self, content: str) -> dict[str, Any]:
        """
        Parse the LLM response to extract thought, action, and action_input.

        Args:
            content: The raw LLM response

        Returns:
            Parsed dict with thought, action, and action_input
        """
        # Try to extract JSON from markdown code blocks
        json_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", content)
        if json_match:
            try:
                return json.loads(json_match.group(1).strip())
            except json.JSONDecodeError:
                pass

        # Try to parse the entire content as JSON
        try:
            return json.loads(content.strip())
        except json.JSONDecodeError:
            pass

        # Fallback: treat as final answer
        return {
            "thought": "Providing direct response",
            "action": "final_answer",
            "action_input": {"answer": content},
        }

    async def _process(
        self,
        message: str,
        context: AgentContext,
    ) -> AsyncIterator[AgentEvent]:
        """
        Process the message using ReAct loop.

        Args:
            message: The user message to process
            context: Execution context

        Yields:
            AgentEvent objects representing the agent's activity
        """
        # Add user message to history
        context.message_history.append(
            LLMMessage(role=MessageRole.USER, content=message)
        )

        iteration = 0
        max_iterations = self.config.max_iterations

        while iteration < max_iterations:
            if context.is_cancelled():
                return

            iteration += 1

            # Step: Thinking
            yield self.emit_step_started("thinking")

            # Build messages for LLM
            system_prompt = self._build_system_prompt(context)
            messages = [
                LLMMessage(role=MessageRole.SYSTEM, content=system_prompt),
                *context.message_history,
            ]

            # Call LLM (streaming) - emit step content for thinking process
            full_content = ""
            async for chunk in self.llm_client.chat_stream(
                messages=messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
            ):
                if context.is_cancelled():
                    return

                if chunk.content:
                    full_content += chunk.content
                    # Emit step content so user can see the thinking process
                    yield self.emit_step_content("thinking", chunk.content)

            yield self.emit_step_finished("thinking")

            # Parse the response
            parsed = self._parse_response(full_content)
            action = parsed.get("action", "final_answer")
            action_input = parsed.get("action_input", {})

            # Add assistant message to history
            context.message_history.append(
                LLMMessage(role=MessageRole.ASSISTANT, content=full_content)
            )

            # Check if this is the final answer
            if action == "final_answer":
                # Emit the final answer with streaming
                answer = action_input.get("answer", full_content)
                final_message_id = str(uuid4())

                yield self.emit_step_started("final_answer")
                yield self.emit_text_start(final_message_id)

                # Stream the answer character by character for a better UX
                # Use chunks of ~10 chars to balance between smooth display and efficiency
                chunk_size = 10
                for i in range(0, len(answer), chunk_size):
                    if context.is_cancelled():
                        return
                    chunk = answer[i : i + chunk_size]
                    yield self.emit_text_content(final_message_id, chunk)
                    # Small delay to create visible streaming effect
                    await asyncio.sleep(0.02)

                yield self.emit_text_end(final_message_id)
                yield self.emit_step_finished("final_answer")

                return

            # Execute tool call
            yield self.emit_step_started("action")

            tool_call_id = str(uuid4())
            yield self.emit_tool_call_start(
                tool_call_id=tool_call_id,
                tool_name=action,
                parent_message_id=None,  # No parent message tracking for now
            )

            # Emit tool arguments
            args_str = json.dumps(action_input)
            yield self.emit_tool_call_args(tool_call_id, args_str)
            yield self.emit_tool_call_end(tool_call_id)

            # Execute the tool
            result = await self.call_tool(
                tool_name=action,
                arguments=action_input,
                tool_call_id=tool_call_id,
            )

            # Emit tool result
            if result.success:
                result_content = result.content
            else:
                result_content = f"Error: {result.error}"

            yield self.emit_tool_call_result(
                tool_call_id=tool_call_id,
                content=result_content,
            )

            yield self.emit_step_finished("action")

            # Add observation to history
            observation_msg = f"Observation: {result_content}"
            context.message_history.append(
                LLMMessage(role=MessageRole.USER, content=observation_msg)
            )

        # Max iterations reached
        yield self.emit_step_started("final")

        final_message_id = str(uuid4())
        fallback_answer = (
            "I've reached the maximum number of reasoning steps. "
            "Based on my analysis, here's what I found:\n\n"
            f"{context.message_history[-1].content if context.message_history else 'Unable to provide a conclusion.'}"
        )

        yield self.emit_text_start(final_message_id)

        # Stream the fallback answer
        chunk_size = 10
        for i in range(0, len(fallback_answer), chunk_size):
            if context.is_cancelled():
                return
            chunk = fallback_answer[i : i + chunk_size]
            yield self.emit_text_content(final_message_id, chunk)
            await asyncio.sleep(0.02)

        yield self.emit_text_end(final_message_id)
        yield self.emit_step_finished("final")
