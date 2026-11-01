"""Persist administrator moderation decisions."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0004_moderation_audit"
down_revision = "0003_roles_moderation"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "moderation_audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("actor_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("character_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("characters.id", ondelete="SET NULL")),
        sa.Column("action", sa.String(16), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_moderation_audit_logs_actor_user_id", "moderation_audit_logs", ["actor_user_id"])
    op.create_index("ix_moderation_audit_logs_character_id", "moderation_audit_logs", ["character_id"])


def downgrade():
    op.drop_index("ix_moderation_audit_logs_character_id", table_name="moderation_audit_logs")
    op.drop_index("ix_moderation_audit_logs_actor_user_id", table_name="moderation_audit_logs")
    op.drop_table("moderation_audit_logs")
