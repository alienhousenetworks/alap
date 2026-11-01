"""Add user character safety reports."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0005_character_reports"
down_revision = "0004_moderation_audit"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "character_reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("reporter_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("character_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("characters.id", ondelete="CASCADE"), nullable=False),
        sa.Column("reason", sa.String(32), nullable=False),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column("status", sa.String(16), nullable=False, server_default="open"),
        sa.Column("resolution_note", sa.Text(), nullable=True),
        sa.Column("reviewed_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_character_reports_reporter_user_id", "character_reports", ["reporter_user_id"])
    op.create_index("ix_character_reports_character_id", "character_reports", ["character_id"])
    op.create_index("ix_character_reports_status_created", "character_reports", ["status", "created_at"])


def downgrade():
    op.drop_index("ix_character_reports_status_created", table_name="character_reports")
    op.drop_index("ix_character_reports_character_id", table_name="character_reports")
    op.drop_index("ix_character_reports_reporter_user_id", table_name="character_reports")
    op.drop_table("character_reports")
