"""
Agent API endpoints.

This module implements the AG-UI (Agent-User Interaction Protocol) endpoints
for running agents and streaming responses via Server-Sent Events.
"""

import asyncio
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base import AgentConfig, AgentContext, Tool
from app.agents.events import RunErrorEvent
from app.agents.factory import AgentFactory
from app.api.deps import get_current_active_user, get_db
from app.core.encryption import decrypt_api_key
from app.integrations.llm.base import LLMConfig, LLMMessage, MessageRole
from app.integrations.llm.factory import LLMClientFactory
from app.models.user import User
from app.schemas.agent import (
    AgentTypeInfo,
    AgentTypesResponse,
    RunAgentInput,
    StopRunResponse,
)
from app.services.llm_model import LLMModelService

router = APIRouter()

# Store for active runs (in production, use Redis)
_active_runs: dict[str, AgentContext] = {}


def get_llm_model_service(db: AsyncSession = Depends(get_db)) -> LLMModelService:
    """Dependency to get LLM model service."""
    return LLMModelService(db)


@router.post("/run")
async def run_agent(
    request: Request,
    input_data: RunAgentInput,
    current_user: User = Depends(get_current_active_user),
    model_service: LLMModelService = Depends(get_llm_model_service),
) -> StreamingResponse:
    """
    Run an agent with the given input.

    This endpoint implements the AG-UI protocol, returning a stream of
    Server-Sent Events (SSE) that represent the agent's activity.

    Args:
        request: FastAPI request object
        input_data: Agent run input data
        current_user: Authenticated user
        model_service: LLM model service

    Returns:
        StreamingResponse with SSE events
    """
    # Generate run_id if not provided
    run_id = input_data.run_id or str(uuid4())
    thread_id = input_data.thread_id

    # Get agent configuration from forwarded_props
    props = input_data.forwarded_props
    agent_type = props.agent_type

    # Create agent context
    context = AgentContext(
        thread_id=thread_id,
        run_id=run_id,
        state=input_data.state,
    )

    # Store active run for cancellation
    _active_runs[run_id] = context

    async def event_generator():
        """Generate SSE events from agent execution."""
        try:
            # Get LLM model configuration
            try:
                if props.model_id:
                    model = await model_service.get_model(current_user, props.model_id)
                else:
                    model = await model_service.get_default_model(current_user)

                if not model:
                    yield RunErrorEvent(
                        message="No LLM model configured. Please add a model in settings.",
                        code="NO_MODEL",
                    ).to_sse()
                    return
            except Exception as e:
                yield RunErrorEvent(
                    message=str(e),
                    code="MODEL_ERROR",
                ).to_sse()
                return

            # Decrypt API key and create LLM client
            try:
                api_key = decrypt_api_key(model.api_key_encrypted)
            except Exception as e:
                yield RunErrorEvent(
                    message=f"Failed to decrypt API key: {e}",
                    code="DECRYPT_ERROR",
                ).to_sse()
                return

            llm_config = LLMConfig(
                model_id=model.model_id,
                api_key=api_key,
                base_url=model.base_url,
                max_tokens=props.max_tokens,
                temperature=props.temperature,
            )

            try:
                llm_client = LLMClientFactory.create(
                    provider=model.provider,
                    config=llm_config,
                )
            except ValueError as e:
                yield RunErrorEvent(
                    message=str(e),
                    code="CLIENT_ERROR",
                ).to_sse()
                return

            # Build tools from input
            tools = [
                Tool(
                    name=t.name,
                    description=t.description,
                    parameters=t.parameters,
                )
                for t in (input_data.tools or [])
            ]

            # Build message history
            for msg in input_data.messages or []:
                role = MessageRole(msg.role)
                context.message_history.append(
                    LLMMessage(
                        role=role,
                        content=msg.content,
                        name=msg.name,
                        tool_call_id=msg.tool_call_id,
                    )
                )

            # Create agent config
            agent_config = AgentConfig(
                temperature=props.temperature,
                max_tokens=props.max_tokens,
                system_prompt=props.system_prompt,
            )

            # Create agent
            try:
                agent = AgentFactory.create(
                    agent_type=agent_type,
                    llm_client=llm_client,
                    tools=tools,
                    config=agent_config,
                    system_prompt=props.system_prompt,
                )
            except ValueError as e:
                yield RunErrorEvent(
                    message=str(e),
                    code="AGENT_ERROR",
                ).to_sse()
                return

            # Get the last user message
            user_messages = [m for m in (input_data.messages or []) if m.role == "user"]
            if not user_messages:
                yield RunErrorEvent(
                    message="No user message provided",
                    code="NO_MESSAGE",
                ).to_sse()
                return

            last_message = user_messages[-1].content

            # Run agent and yield events
            async for event in agent.run(last_message, context):
                if await request.is_disconnected():
                    context.cancel()
                    break
                yield event.to_sse()

        except asyncio.CancelledError:
            yield RunErrorEvent(
                message="Run cancelled",
                code="RUN_CANCELLED",
            ).to_sse()
        except Exception as e:
            import traceback

            error_trace = traceback.format_exc()
            print(f"Agent error: {error_trace}")  # Log full traceback
            yield RunErrorEvent(
                message=str(e),
                code="INTERNAL_ERROR",
            ).to_sse()
        finally:
            # Clean up active run
            _active_runs.pop(run_id, None)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )


@router.post("/run/{run_id}/stop", response_model=dict[str, Any])
async def stop_run(
    run_id: str,
    current_user: User = Depends(get_current_active_user),
) -> dict[str, Any]:
    """
    Stop a running agent.

    Args:
        run_id: The run ID to stop
        current_user: Authenticated user

    Returns:
        Stop result
    """
    context = _active_runs.get(run_id)

    if context:
        context.cancel()
        return {
            "code": 0,
            "message": "success",
            "data": StopRunResponse(run_id=run_id, stopped=True).model_dump(),
        }
    else:
        return {
            "code": 0,
            "message": "success",
            "data": StopRunResponse(run_id=run_id, stopped=False).model_dump(),
        }


@router.get("/types", response_model=dict[str, Any])
async def list_agent_types(
    current_user: User = Depends(get_current_active_user),
) -> dict[str, Any]:
    """
    List available agent types.

    Args:
        current_user: Authenticated user

    Returns:
        List of agent types
    """
    types = []
    for agent_type in AgentFactory.list_types():
        info = AgentFactory.get_agent_info(agent_type)
        types.append(
            AgentTypeInfo(
                type=info["type"],
                name=info["name"],
                description=info["description"],
            )
        )

    return {
        "code": 0,
        "message": "success",
        "data": AgentTypesResponse(items=types).model_dump(),
    }
