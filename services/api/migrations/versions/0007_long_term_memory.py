"""Add opt-in encrypted per-user, per-character long-term memory.

Revision ID: 0007
Revises: 0006
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("memory_enabled", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.create_table(
        "character_memories",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("character_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("characters.id", ondelete="CASCADE"), nullable=False),
        sa.Column("category", sa.String(length=32), nullable=False),
        sa.Column("encrypted_content", sa.Text(), nullable=False),
        sa.Column("fingerprint", sa.String(length=64), nullable=False),
        sa.Column("importance", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("source_message_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("conversation_messages.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("user_id", "character_id", "fingerprint", name="uq_memory_scope_fingerprint"),
    )
    op.create_index("ix_character_memories_user_id", "character_memories", ["user_id"])
    op.create_index("ix_character_memories_character_id", "character_memories", ["character_id"])


def downgrade() -> None:
    op.drop_index("ix_character_memories_character_id", table_name="character_memories")
    op.drop_index("ix_character_memories_user_id", table_name="character_memories")
    op.drop_table("character_memories")
    op.drop_column("users", "memory_enabled")
