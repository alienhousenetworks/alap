"""Add private generated media asset metadata.

Revision ID: 0008
Revises: 0007
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "media_assets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("media_type", sa.String(length=16), nullable=False),
        sa.Column("object_key", sa.String(length=512), nullable=False, unique=True),
        sa.Column("mime_type", sa.String(length=100), nullable=False),
        sa.Column("byte_size", sa.Integer(), nullable=False),
        sa.Column("provider", sa.String(length=40), nullable=False),
        sa.Column("model", sa.String(length=120), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_media_assets_user_id", "media_assets", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_media_assets_user_id", table_name="media_assets")
    op.drop_table("media_assets")
