"""
Session service for managing chat sessions and messages.
"""

from typing import Optional
from uuid import UUID

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppError
from app.models.message import ChatMessage
from app.models.session import ChatSession
from app.schemas.message import MessageCreateSchema, MessageListSchema, MessageSchema
from app.schemas.session import (
    SessionCreateSchema,
    SessionListSchema,
    SessionSchema,
    SessionUpdateSchema,
)


class SessionService:
    """Service for managing chat sessions and messages."""

    def __init__(self, db: AsyncSession):
        """Initialize session service.

        Args:
            db: Database session
        """
        self.db = db

    async def create_session(
        self,
        user_id: UUID,
        data: SessionCreateSchema,
    ) -> SessionSchema:
        """Create a new chat session.

        Args:
            user_id: User ID
            data: Session creation data

        Returns:
            Created session
        """
        # Convert settings to dict
        settings_dict = data.settings.model_dump() if data.settings else {}

        # Create session
        session = ChatSession(
            user_id=user_id,
            title=data.title or "New Chat",
            agent_type=data.agent_type,
            model_config_id=data.model_config_id,
            settings=settings_dict,
        )

        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)

        return SessionSchema.model_validate(session)

    async def list_sessions(
        self,
        user_id: UUID,
        page: int = 1,
        page_size: int = 20,
    ) -> SessionListSchema:
        """List user's chat sessions.

        Args:
            user_id: User ID
            page: Page number (1-indexed)
            page_size: Items per page

        Returns:
            Paginated session list
        """
        # Validate pagination
        if page < 1:
            raise AppError(40000, "Page must be >= 1", 400)
        if page_size < 1 or page_size > 100:
            raise AppError(40000, "Page size must be between 1 and 100", 400)

        # Count total
        count_query = select(func.count(ChatSession.id)).where(
            ChatSession.user_id == user_id,
            ChatSession.is_deleted == False,  # noqa: E712
        )
        total = await self.db.scalar(count_query) or 0

        # Fetch sessions
        offset = (page - 1) * page_size
        query = (
            select(ChatSession)
            .where(
                ChatSession.user_id == user_id,
                ChatSession.is_deleted == False,  # noqa: E712
            )
            .order_by(desc(ChatSession.updated_at))
            .offset(offset)
            .limit(page_size)
        )

        result = await self.db.execute(query)
        sessions = result.scalars().all()

        return SessionListSchema(
            items=[SessionSchema.model_validate(s) for s in sessions],
            total=total,
            page=page,
            page_size=page_size,
        )

    async def get_session(
        self,
        session_id: UUID,
        user_id: UUID,
    ) -> SessionSchema:
        """Get a specific session.

        Args:
            session_id: Session ID
            user_id: User ID (for authorization)

        Returns:
            Session details

        Raises:
            AppError: If session not found or unauthorized
        """
        query = select(ChatSession).where(
            ChatSession.id == session_id,
            ChatSession.user_id == user_id,
            ChatSession.is_deleted == False,  # noqa: E712
        )

        result = await self.db.execute(query)
        session = result.scalar_one_or_none()

        if not session:
            raise AppError(40400, "Session not found", 404)

        return SessionSchema.model_validate(session)

    async def update_session(
        self,
        session_id: UUID,
        user_id: UUID,
        data: SessionUpdateSchema,
    ) -> SessionSchema:
        """Update a session.

        Args:
            session_id: Session ID
            user_id: User ID (for authorization)
            data: Update data

        Returns:
            Updated session

        Raises:
            AppError: If session not found or unauthorized
        """
        # Fetch session
        query = select(ChatSession).where(
            ChatSession.id == session_id,
            ChatSession.user_id == user_id,
            ChatSession.is_deleted == False,  # noqa: E712
        )

        result = await self.db.execute(query)
        session = result.scalar_one_or_none()

        if not session:
            raise AppError(40400, "Session not found", 404)

        # Update fields
        update_data = data.model_dump(exclude_unset=True)

        # Handle settings separately
        if "settings" in update_data and update_data["settings"] is not None:
            update_data["settings"] = update_data["settings"].model_dump()

        for field, value in update_data.items():
            setattr(session, field, value)

        await self.db.commit()
        await self.db.refresh(session)

        return SessionSchema.model_validate(session)

    async def delete_session(
        self,
        session_id: UUID,
        user_id: UUID,
    ) -> None:
        """Delete a session (soft delete).

        Args:
            session_id: Session ID
            user_id: User ID (for authorization)

        Raises:
            AppError: If session not found or unauthorized
        """
        # Fetch session
        query = select(ChatSession).where(
            ChatSession.id == session_id,
            ChatSession.user_id == user_id,
            ChatSession.is_deleted == False,  # noqa: E712
        )

        result = await self.db.execute(query)
        session = result.scalar_one_or_none()

        if not session:
            raise AppError(40400, "Session not found", 404)

        # Soft delete
        session.is_deleted = True
        await self.db.commit()

    async def add_message(
        self,
        session_id: UUID,
        user_id: UUID,
        data: MessageCreateSchema,
    ) -> MessageSchema:
        """Add a message to a session.

        Args:
            session_id: Session ID
            user_id: User ID (for authorization)
            data: Message data

        Returns:
            Created message

        Raises:
            AppError: If session not found or unauthorized
        """
        # Verify session exists and belongs to user
        query = select(ChatSession).where(
            ChatSession.id == session_id,
            ChatSession.user_id == user_id,
            ChatSession.is_deleted == False,  # noqa: E712
        )

        result = await self.db.execute(query)
        session = result.scalar_one_or_none()

        if not session:
            raise AppError(40400, "Session not found", 404)

        # Create message
        message = ChatMessage(
            session_id=session_id,
            role=data.role,
            content=data.content,
            meta=data.meta,
        )

        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)

        return MessageSchema.model_validate(message)

    async def list_messages(
        self,
        session_id: UUID,
        user_id: UUID,
        page: int = 1,
        page_size: int = 20,
    ) -> MessageListSchema:
        """List messages in a session.

        Args:
            session_id: Session ID
            user_id: User ID (for authorization)
            page: Page number (1-indexed)
            page_size: Items per page

        Returns:
            Paginated message list

        Raises:
            AppError: If session not found or unauthorized
        """
        # Verify session exists and belongs to user
        query = select(ChatSession).where(
            ChatSession.id == session_id,
            ChatSession.user_id == user_id,
            ChatSession.is_deleted == False,  # noqa: E712
        )

        result = await self.db.execute(query)
        session = result.scalar_one_or_none()

        if not session:
            raise AppError(40400, "Session not found", 404)

        # Validate pagination
        if page < 1:
            raise AppError(40000, "Page must be >= 1", 400)
        if page_size < 1 or page_size > 100:
            raise AppError(40000, "Page size must be between 1 and 100", 400)

        # Count total messages
        count_query = select(func.count(ChatMessage.id)).where(
            ChatMessage.session_id == session_id
        )
        total = await self.db.scalar(count_query) or 0

        # Fetch messages
        offset = (page - 1) * page_size
        messages_query = (
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at)
            .offset(offset)
            .limit(page_size)
        )

        result = await self.db.execute(messages_query)
        messages = result.scalars().all()

        return MessageListSchema(
            items=[MessageSchema.model_validate(m) for m in messages],
            total=total,
            page=page,
            page_size=page_size,
        )
