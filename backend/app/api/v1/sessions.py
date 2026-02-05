"""
Session API endpoints.
"""

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, get_db
from app.core.exceptions import AppError
from app.models.user import User
from app.schemas.message import MessageCreateSchema, MessageListSchema, MessageSchema
from app.schemas.session import (
    SessionCreateSchema,
    SessionListSchema,
    SessionSchema,
    SessionUpdateSchema,
)
from app.services.session import SessionService

router = APIRouter()


def get_session_service(db: AsyncSession = Depends(get_db)) -> SessionService:
    """Dependency to get session service."""
    return SessionService(db)


@router.post("", response_model=dict[str, Any])
async def create_session(
    data: SessionCreateSchema,
    current_user: User = Depends(get_current_active_user),
    service: SessionService = Depends(get_session_service),
) -> dict[str, Any]:
    """Create a new chat session.

    Args:
        data: Session creation data
        current_user: Current authenticated user
        service: Session service

    Returns:
        Standard response with created session
    """
    try:
        session = await service.create_session(current_user.id, data)
        return {
            "code": 0,
            "message": "success",
            "data": session.model_dump(),
        }
    except AppError as e:
        return {
            "code": e.code,
            "message": e.message,
            "data": None,
        }


@router.get("", response_model=dict[str, Any])
async def list_sessions(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_active_user),
    service: SessionService = Depends(get_session_service),
) -> dict[str, Any]:
    """List user's chat sessions.

    Args:
        page: Page number (1-indexed)
        page_size: Items per page
        current_user: Current authenticated user
        service: Session service

    Returns:
        Standard response with paginated session list
    """
    try:
        sessions = await service.list_sessions(current_user.id, page, page_size)
        return {
            "code": 0,
            "message": "success",
            "data": sessions.model_dump(),
        }
    except AppError as e:
        return {
            "code": e.code,
            "message": e.message,
            "data": None,
        }


@router.get("/{session_id}", response_model=dict[str, Any])
async def get_session(
    session_id: UUID,
    current_user: User = Depends(get_current_active_user),
    service: SessionService = Depends(get_session_service),
) -> dict[str, Any]:
    """Get session details.

    Args:
        session_id: Session ID
        current_user: Current authenticated user
        service: Session service

    Returns:
        Standard response with session details
    """
    try:
        session = await service.get_session(session_id, current_user.id)
        return {
            "code": 0,
            "message": "success",
            "data": session.model_dump(),
        }
    except AppError as e:
        return {
            "code": e.code,
            "message": e.message,
            "data": None,
        }


@router.put("/{session_id}", response_model=dict[str, Any])
async def update_session(
    session_id: UUID,
    data: SessionUpdateSchema,
    current_user: User = Depends(get_current_active_user),
    service: SessionService = Depends(get_session_service),
) -> dict[str, Any]:
    """Update a session.

    Args:
        session_id: Session ID
        data: Update data
        current_user: Current authenticated user
        service: Session service

    Returns:
        Standard response with updated session
    """
    try:
        session = await service.update_session(session_id, current_user.id, data)
        return {
            "code": 0,
            "message": "success",
            "data": session.model_dump(),
        }
    except AppError as e:
        return {
            "code": e.code,
            "message": e.message,
            "data": None,
        }


@router.delete("/{session_id}", response_model=dict[str, Any])
async def delete_session(
    session_id: UUID,
    current_user: User = Depends(get_current_active_user),
    service: SessionService = Depends(get_session_service),
) -> dict[str, Any]:
    """Delete a session (soft delete).

    Args:
        session_id: Session ID
        current_user: Current authenticated user
        service: Session service

    Returns:
        Standard response
    """
    try:
        await service.delete_session(session_id, current_user.id)
        return {
            "code": 0,
            "message": "success",
            "data": None,
        }
    except AppError as e:
        return {
            "code": e.code,
            "message": e.message,
            "data": None,
        }


@router.post("/{session_id}/messages", response_model=dict[str, Any])
async def add_message(
    session_id: UUID,
    data: MessageCreateSchema,
    current_user: User = Depends(get_current_active_user),
    service: SessionService = Depends(get_session_service),
) -> dict[str, Any]:
    """Add a message to a session.

    Args:
        session_id: Session ID
        data: Message data
        current_user: Current authenticated user
        service: Session service

    Returns:
        Standard response with created message
    """
    try:
        message = await service.add_message(session_id, current_user.id, data)
        return {
            "code": 0,
            "message": "success",
            "data": message.model_dump(),
        }
    except AppError as e:
        return {
            "code": e.code,
            "message": e.message,
            "data": None,
        }


@router.get("/{session_id}/messages", response_model=dict[str, Any])
async def list_messages(
    session_id: UUID,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_active_user),
    service: SessionService = Depends(get_session_service),
) -> dict[str, Any]:
    """List messages in a session.

    Args:
        session_id: Session ID
        page: Page number (1-indexed)
        page_size: Items per page
        current_user: Current authenticated user
        service: Session service

    Returns:
        Standard response with paginated message list
    """
    try:
        messages = await service.list_messages(
            session_id, current_user.id, page, page_size
        )
        return {
            "code": 0,
            "message": "success",
            "data": messages.model_dump(),
        }
    except AppError as e:
        return {
            "code": e.code,
            "message": e.message,
            "data": None,
        }
