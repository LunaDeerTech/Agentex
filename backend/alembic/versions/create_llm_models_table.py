"""Create LLM models table.

Revision ID: create_llm_models_table
Revises: bd6fcbea44b8
Create Date: 2026-02-04
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "create_llm_models"
down_revision: str | None = "bd6fcbea44b8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create llm_models table."""
    op.create_table(
        "llm_models",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("provider", sa.String(50), nullable=False, index=True),
        sa.Column("model_id", sa.String(100), nullable=False),
        sa.Column("base_url", sa.String(500), nullable=True),
        sa.Column("api_key_encrypted", sa.Text(), nullable=False),
        sa.Column("max_tokens", sa.Integer(), nullable=False, server_default="4096"),
        sa.Column("temperature", sa.Float(), nullable=False, server_default="0.7"),
        sa.Column("top_p", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("is_enabled", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("is_default", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "is_deleted",
            sa.Boolean(),
            nullable=False,
            server_default="false",
            index=True,
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_llm_models_user_id",
            ondelete="CASCADE",
        ),
    )

    # Create index for finding default model quickly
    op.create_index(
        "ix_llm_models_user_default",
        "llm_models",
        ["user_id", "is_default"],
        unique=False,
    )


def downgrade() -> None:
    """Drop llm_models table."""
    op.drop_index("ix_llm_models_user_default", table_name="llm_models")
    op.drop_table("llm_models")
