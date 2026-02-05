"""
Chat message model.
"""

from typing import TYPE_CHECKING

from sqlalchemy import UUID, Column, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from .base import BaseModel

if TYPE_CHECKING:
    from app.models.session import ChatSession


class ChatMessage(BaseModel):
    """Chat message model."""

    __tablename__ = "chat_messages"

    # Foreign keys
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("chat_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Message content
    role = Column(String(20), nullable=False)  # user, assistant, system, tool
    content = Column(Text, nullable=False)

    # Meta information stored as JSONB (tool calls, thinking process, etc.)
    meta = Column(JSONB, nullable=False, default={})

    # Relationships
    session = relationship("ChatSession", back_populates="messages")

    # Index for efficient queries
    __table_args__ = (
        Index("idx_chat_messages_session_created", "session_id", "created_at"),
    )

    def __repr__(self):
        return f"<ChatMessage(id={self.id}, session_id={self.session_id}, role={self.role})>"
