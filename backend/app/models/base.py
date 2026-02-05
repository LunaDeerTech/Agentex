"""Base model classes with common fields."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class TimestampMixin:
    """Mixin that adds timestamp fields to a model."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Creation timestamp",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Last update timestamp",
    )


class SoftDeleteMixin:
    """Mixin that adds soft delete functionality to a model."""

    is_deleted: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
        index=True,
        comment="Soft delete flag",
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Deletion timestamp",
    )


class BaseModel(Base, TimestampMixin, SoftDeleteMixin):
    """
    Base model class with UUID primary key, timestamps, and soft delete.

    All models should inherit from this class to get:
    - id: UUID primary key
    - created_at: Creation timestamp
    - updated_at: Last update timestamp
    - is_deleted: Soft delete flag
    - deleted_at: Deletion timestamp

    Example:
        class User(BaseModel):
            __tablename__ = "users"

            username: Mapped[str] = mapped_column(String(50), unique=True)
            email: Mapped[str] = mapped_column(String(255), unique=True)
    """

    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Primary key (UUID)",
    )

    def __repr__(self) -> str:
        """String representation of the model."""
        return f"<{self.__class__.__name__}(id={self.id})>"

    def to_dict(self) -> dict[str, Any]:
        """
        Convert model instance to dictionary.

        Returns:
            Dictionary with all column values
        """
        return {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }
