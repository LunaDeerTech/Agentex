"""
Plan and Execute Agent implementation.

PlanAndExecute is an agent architecture that separates planning from execution.
It first creates a detailed plan to solve a complex task, then executes each
step while monitoring progress and adjusting the plan as needed.

Key features:
- Task decomposition into subtasks
- Dependency management between tasks
- Progress tracking
- Dynamic re-planning based on results
"""

import json
import re
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from uuid import uuid4

from app.agents.base import AgentConfig, AgentContext, BaseAgent, Tool
from app.agents.events import AgentEvent, StateDeltaEvent, StateSnapshotEvent
from app.integrations.llm.base import BaseLLMClient, LLMMessage, MessageRole


class TaskStatus(str, Enum):
    """Status of a task in the plan."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class Task:
    """Represents a single task in the plan."""

    id: str
    title: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    dependencies: list[str] = field(default_factory=list)
    result: str | None = None
    error: str | None = None
    tool_calls: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert task to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "dependencies": self.dependencies,
            "result": self.result,
            "error": self.error,
        }


@dataclass
class Plan:
    """Represents the execution plan."""

    goal: str
    tasks: list[Task] = field(default_factory=list)
    current_task_index: int = 0
    revision: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert plan to dictionary."""
        return {
            "goal": self.goal,
            "tasks": [t.to_dict() for t in self.tasks],
            "current_task_index": self.current_task_index,
            "revision": self.revision,
        }

    def get_next_executable_task(self) -> Task | None:
        """Get the next task that can be executed."""
        for task in self.tasks:
            if task.status == TaskStatus.PENDING:
                # Check if all dependencies are completed
                deps_met = all(
                    any(
                        t.id == dep_id and t.status == TaskStatus.COMPLETED
                        for t in self.tasks
                    )
                    for dep_id in task.dependencies
                )
                if deps_met:
                    return task
        return None

    def is_complete(self) -> bool:
        """Check if all tasks are completed or skipped."""
        return all(
            t.status in (TaskStatus.COMPLETED, TaskStatus.SKIPPED, TaskStatus.FAILED)
            for t in self.tasks
        )

    def get_completed_results(self) -> str:
        """Get summary of completed task results."""
        results = []
        for task in self.tasks:
            if task.status == TaskStatus.COMPLETED and task.result:
                results.append(f"[{task.title}]: {task.result}")
        return "\n".join(results) if results else "No completed tasks yet."


@dataclass
class PlanExecuteConfig(AgentConfig):
    """Configuration specific to Plan and Execute Agent."""

    max_planning_attempts: int = 3
    max_execution_retries: int = 2
    allow_replanning: bool = True
    max_tasks_per_plan: int = 10


PLANNING_SYSTEM_PROMPT = """You are a planning agent that breaks down complex tasks into manageable steps.

## Your Task
Given a user request, create a detailed plan to accomplish it.

## Available Tools
{tools_description}

## Planning Guidelines

1. **Analyze the Goal**: Understand what the user wants to achieve
2. **Break Down**: Divide the task into smaller, actionable subtasks
3. **Order Tasks**: Arrange tasks in logical order with dependencies
4. **Be Specific**: Each task should have a clear, measurable outcome
5. **Consider Tools**: Plan which tools will be needed for each task

## Response Format

Respond with a JSON plan:
```json
{{
    "goal": "Summary of the overall goal",
    "tasks": [
        {{
            "id": "task_1",
            "title": "Short task title",
            "description": "Detailed description of what to do",
            "dependencies": []
        }},
        {{
            "id": "task_2",
            "title": "Another task",
            "description": "Depends on task_1",
            "dependencies": ["task_1"]
        }}
    ]
}}
```

## Important Rules
- Maximum {max_tasks} tasks per plan
- Each task should be completable with available tools
- Tasks should be independent when possible (fewer dependencies)
- Include a final task to synthesize results
"""

EXECUTION_SYSTEM_PROMPT = """You are an execution agent working on a specific task.

## Current Plan
Goal: {goal}
Progress: {progress}

## Your Current Task
ID: {task_id}
Title: {task_title}
Description: {task_description}

## Previous Task Results
{previous_results}

## Available Tools
{tools_description}

## Instructions

Execute the current task. You can:
1. Use a tool to accomplish part of the task
2. Complete the task with a final result

## Response Format

To use a tool:
```json
{{
    "action": "tool",
    "tool_name": "name_of_tool",
    "tool_input": {{"param": "value"}}
}}
```

To complete the task:
```json
{{
    "action": "complete",
    "result": "Description of what was accomplished"
}}
```

If the task cannot be completed:
```json
{{
    "action": "fail",
    "reason": "Why the task failed"
}}
```
"""

SYNTHESIS_SYSTEM_PROMPT = """You are synthesizing the results of a completed plan.

## Goal
{goal}

## Completed Tasks and Results
{task_results}

## Instructions
Provide a comprehensive summary that:
1. Answers the user's original request
2. Highlights key findings or actions taken
3. Notes any issues or limitations encountered

Be clear, concise, and helpful.
"""


class PlanAndExecuteAgent(BaseAgent):
    """
    Plan and Execute Agent implementation.

    This agent first creates a plan to solve a complex task, then
    executes each step while tracking progress and adjusting as needed.
    """

    def __init__(
        self,
        llm_client: BaseLLMClient,
        tools: list[Tool] | None = None,
        config: AgentConfig | None = None,
        system_prompt: str | None = None,
    ):
        """
        Initialize the Plan and Execute agent.

        Args:
            llm_client: LLM client for model calls
            tools: Optional list of tools available to the agent
            config: Optional configuration (AgentConfig or PlanExecuteConfig)
            system_prompt: Optional custom system prompt
        """
        # Create PlanExecuteConfig from AgentConfig if needed
        if config is None:
            pe_config = PlanExecuteConfig()
        elif isinstance(config, PlanExecuteConfig):
            pe_config = config
        else:
            # Convert AgentConfig to PlanExecuteConfig
            pe_config = PlanExecuteConfig(
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                max_iterations=config.max_iterations,
                system_prompt=config.system_prompt,
            )

        super().__init__(llm_client, tools, pe_config)
        self._custom_system_prompt = system_prompt
        self._pe_config = pe_config

    @property
    def agent_type(self) -> str:
        return "plan_execute"

    def _get_tools_description(self) -> str:
        """Build tools description string."""
        if not self.tools:
            return "No tools available. Complete tasks using reasoning only."

        return "\n".join(
            [
                f"- **{tool.name}**: {tool.description}\n"
                f"  Parameters: {json.dumps(tool.parameters)}"
                for tool in (self.tools or [])
            ]
        )

    def _build_planning_prompt(self) -> str:
        """Build the planning phase system prompt."""
        return PLANNING_SYSTEM_PROMPT.format(
            tools_description=self._get_tools_description(),
            max_tasks=self._pe_config.max_tasks_per_plan,
        )

    def _build_execution_prompt(self, plan: Plan, task: Task) -> str:
        """Build the execution phase system prompt."""
        # Calculate progress
        completed = sum(1 for t in plan.tasks if t.status == TaskStatus.COMPLETED)
        total = len(plan.tasks)
        progress = f"{completed}/{total} tasks completed"

        return EXECUTION_SYSTEM_PROMPT.format(
            goal=plan.goal,
            progress=progress,
            task_id=task.id,
            task_title=task.title,
            task_description=task.description,
            previous_results=plan.get_completed_results(),
            tools_description=self._get_tools_description(),
        )

    def _build_synthesis_prompt(self, plan: Plan) -> str:
        """Build the synthesis phase system prompt."""
        task_results = "\n\n".join(
            [
                f"### {t.title}\n"
                f"Status: {t.status.value}\n"
                f"Result: {t.result or 'N/A'}"
                for t in plan.tasks
            ]
        )

        return SYNTHESIS_SYSTEM_PROMPT.format(
            goal=plan.goal,
            task_results=task_results,
        )

    def _parse_plan(self, content: str) -> Plan | None:
        """Parse the planning LLM response into a Plan object."""
        # Extract JSON from markdown code blocks
        json_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", content)
        json_str = json_match.group(1).strip() if json_match else content.strip()

        try:
            data = json.loads(json_str)
        except json.JSONDecodeError:
            return None

        if "goal" not in data or "tasks" not in data:
            return None

        tasks = []
        for task_data in data["tasks"][: self._pe_config.max_tasks_per_plan]:
            tasks.append(
                Task(
                    id=task_data.get("id", str(uuid4())[:8]),
                    title=task_data.get("title", "Untitled Task"),
                    description=task_data.get("description", ""),
                    dependencies=task_data.get("dependencies", []),
                )
            )

        return Plan(goal=data["goal"], tasks=tasks)

    def _parse_execution_response(self, content: str) -> dict[str, Any]:
        """Parse the execution LLM response."""
        json_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", content)
        json_str = json_match.group(1).strip() if json_match else content.strip()

        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            # Treat as direct completion
            return {"action": "complete", "result": content}

    async def _process(
        self,
        message: str,
        context: AgentContext,
    ) -> AsyncIterator[AgentEvent]:
        """
        Process the message using Plan and Execute pattern.

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

        # ============ Planning Phase ============
        yield self.emit_step_started("planning")

        planning_prompt = self._build_planning_prompt()
        # Include conversation history for context (last 10 messages before current)
        messages = [
            LLMMessage(role=MessageRole.SYSTEM, content=planning_prompt),
            *context.message_history[:-1][-10:],  # Last 10 historical messages
            LLMMessage(role=MessageRole.USER, content=message),
        ]

        # Generate plan (send content to step, not as message)
        full_content = ""
        async for chunk in self.llm_client.chat_stream(
            messages=messages,
            temperature=0.3,  # Lower temperature for planning
            max_tokens=self.config.max_tokens,
        ):
            if context.is_cancelled():
                return

            if chunk.content:
                full_content += chunk.content
                # Send as step content (thinking), not as message
                yield self.emit_step_content("planning", chunk.content)

        # Parse the plan
        plan = self._parse_plan(full_content)
        if not plan:
            yield self.emit_step_finished("planning")
            # Fallback to direct answer
            final_id = str(uuid4())
            yield self.emit_text_start(final_id)
            yield self.emit_text_content(
                final_id,
                "I couldn't create a structured plan. Let me answer directly:\n\n"
                + full_content,
            )
            yield self.emit_text_end(final_id)
            return

        yield self.emit_step_finished("planning")

        # Emit plan state
        yield StateSnapshotEvent(snapshot={"plan": plan.to_dict()})

        # ============ Execution Phase ============
        while not plan.is_complete():
            if context.is_cancelled():
                return

            task = plan.get_next_executable_task()
            if not task:
                # No executable tasks (might have circular dependencies)
                break

            # Update task status
            task.status = TaskStatus.IN_PROGRESS
            yield StateDeltaEvent(
                delta=[
                    {
                        "op": "replace",
                        "path": f"/plan/tasks/{plan.tasks.index(task)}/status",
                        "value": "in_progress",
                    }
                ]
            )

            yield self.emit_step_started(f"executing:{task.id}")

            # Build execution prompt
            execution_prompt = self._build_execution_prompt(plan, task)
            # Include conversation history for context
            exec_messages = [
                LLMMessage(role=MessageRole.SYSTEM, content=execution_prompt),
                *context.message_history[-5:],  # Last 5 messages for context
            ]

            retry_count = 0
            task_completed = False
            step_name = f"executing:{task.id}"

            while (
                not task_completed
                and retry_count <= self._pe_config.max_execution_retries
            ):
                if context.is_cancelled():
                    return

                exec_content = ""
                async for chunk in self.llm_client.chat_stream(
                    messages=exec_messages,
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens,
                ):
                    if context.is_cancelled():
                        return

                    if chunk.content:
                        exec_content += chunk.content
                        # Send execution content to step, not as message
                        yield self.emit_step_content(step_name, chunk.content)

                # Parse execution response
                response = self._parse_execution_response(exec_content)
                action = response.get("action", "complete")

                if action == "tool":
                    # Execute tool call
                    tool_name = response.get("tool_name", "")
                    tool_input = response.get("tool_input", {})

                    tool_call_id = str(uuid4())
                    yield self.emit_tool_call_start(
                        tool_call_id=tool_call_id,
                        tool_name=tool_name,
                        parent_message_id=None,
                    )
                    yield self.emit_tool_call_args(
                        tool_call_id,
                        json.dumps(tool_input),
                    )
                    yield self.emit_tool_call_end(tool_call_id)

                    # Execute the tool
                    result = await self.call_tool(
                        tool_name=tool_name,
                        arguments=tool_input,
                        tool_call_id=tool_call_id,
                    )

                    if result.success:
                        result_content = result.content
                    else:
                        result_content = f"Error: {result.error}"

                    yield self.emit_tool_call_result(
                        tool_call_id=tool_call_id,
                        content=result_content,
                    )

                    # Add to execution messages for next iteration
                    exec_messages.append(
                        LLMMessage(role=MessageRole.ASSISTANT, content=exec_content)
                    )
                    exec_messages.append(
                        LLMMessage(
                            role=MessageRole.USER,
                            content=f"Tool result: {result_content}",
                        )
                    )

                    task.tool_calls.append(tool_name)
                    retry_count += 1

                elif action == "complete":
                    task.status = TaskStatus.COMPLETED
                    task.result = response.get("result", exec_content)
                    task_completed = True

                elif action == "fail":
                    task.status = TaskStatus.FAILED
                    task.error = response.get("reason", "Task failed")
                    task_completed = True

                else:
                    # Unknown action, treat as complete
                    task.status = TaskStatus.COMPLETED
                    task.result = exec_content
                    task_completed = True

            # If we exhausted retries without completing
            if not task_completed:
                task.status = TaskStatus.FAILED
                task.error = "Maximum retries exceeded"

            yield self.emit_step_finished(f"executing:{task.id}")

            # Update state
            yield StateDeltaEvent(
                delta=[
                    {
                        "op": "replace",
                        "path": f"/plan/tasks/{plan.tasks.index(task)}",
                        "value": task.to_dict(),
                    }
                ]
            )

        # ============ Synthesis Phase ============
        yield self.emit_step_started("synthesis")

        synthesis_prompt = self._build_synthesis_prompt(plan)
        # Include conversation history to maintain context in final answer
        synthesis_messages = [
            LLMMessage(role=MessageRole.SYSTEM, content=synthesis_prompt),
            *context.message_history[-5:],  # Last 5 messages for context
        ]

        final_message_id = str(uuid4())
        yield self.emit_text_start(final_message_id)

        async for chunk in self.llm_client.chat_stream(
            messages=synthesis_messages,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
        ):
            if context.is_cancelled():
                yield self.emit_text_end(final_message_id)
                return

            if chunk.content:
                yield self.emit_text_content(final_message_id, chunk.content)

        yield self.emit_text_end(final_message_id)
        yield self.emit_step_finished("synthesis")

        # Final state
        yield StateSnapshotEvent(
            snapshot={"plan": plan.to_dict(), "status": "completed"}
        )
