"""
Chat session model.
"""

from sqlalchemy import UUID, Boolean, Column, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from .base import BaseModel


class ChatSession(BaseModel):
    """Chat session model."""

    __tablename__ = "chat_sessions"

    # Foreign keys
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Basic info
    title = Column(String(200), nullable=True)

    # Agent configuration
    agent_type = Column(
        String(50), nullable=False, default="react"
    )  # react, agentic_rag, plan_execute
    model_config_id = Column(
        UUID(as_uuid=True),
        ForeignKey("llm_models.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Settings stored as JSONB
    settings = Column(JSONB, nullable=False, default={})

    # Soft delete
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)

    # Relationships
    user = relationship("User")
    model_config = relationship("LLMModel")
    messages = relationship(
        "ChatMessage", back_populates="session", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return (
            f"<ChatSession(id={self.id}, user_id={self.user_id}, title={self.title})>"
        )
