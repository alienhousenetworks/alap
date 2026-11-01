"""Opt-in user memory, private media metadata and provider spend reservations."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0007_memory_media"
down_revision = "0006_unique_open_reports"
branch_labels = None
depends_on = None

def upgrade():
    op.add_column("users", sa.Column("memory_enabled", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.create_table(
        "user_memories",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("category", sa.String(32), nullable=False, server_default="preference"),
        sa.Column("source", sa.String(24), nullable=False, server_default="user"),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_user_memories_user_id", "user_memories", ["user_id"])
    op.create_index("ix_user_memories_user_enabled", "user_memories", ["user_id", "enabled"])
    op.create_table(
        "media_assets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("conversations.id", ondelete="SET NULL"), nullable=True),
        sa.Column("kind", sa.String(16), nullable=False),
        sa.Column("object_key", sa.String(512), nullable=False, unique=True),
        sa.Column("mime_type", sa.String(100), nullable=False),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("provider", sa.String(40), nullable=False),
        sa.Column("model", sa.String(120), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_media_assets_user_id", "media_assets", ["user_id"])
    op.create_index("ix_media_assets_conversation_id", "media_assets", ["conversation_id"])
    op.create_table(
        "media_daily_usage",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("usage_date", sa.Date(), nullable=False),
        sa.Column("image_count", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("voice_characters", sa.BigInteger(), nullable=False, server_default="0"),
        sa.UniqueConstraint("user_id", "usage_date", name="uq_media_daily_user_date"),
    )
    op.create_index("ix_media_daily_usage_user_id", "media_daily_usage", ["user_id"])
    op.create_table(
        "media_monthly_budgets",
        sa.Column("month", sa.String(7), primary_key=True),
        sa.Column("spent_usd", sa.Numeric(12, 6), nullable=False, server_default="0"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

def downgrade():
    op.drop_table("media_monthly_budgets")
    op.drop_index("ix_media_daily_usage_user_id", table_name="media_daily_usage")
    op.drop_table("media_daily_usage")
    op.drop_index("ix_media_assets_conversation_id", table_name="media_assets")
    op.drop_index("ix_media_assets_user_id", table_name="media_assets")
    op.drop_table("media_assets")
    op.drop_index("ix_user_memories_user_enabled", table_name="user_memories")
    op.drop_index("ix_user_memories_user_id", table_name="user_memories")
    op.drop_table("user_memories")
    op.drop_column("users", "memory_enabled")
