"""Prevent duplicate open reports per user and character."""
from alembic import op
import sqlalchemy as sa

revision = "0006_unique_open_reports"
down_revision = "0005_character_reports"
branch_labels = None
depends_on = None


def upgrade():
    op.create_index(
        "uq_character_reports_open_user_character",
        "character_reports",
        ["reporter_user_id", "character_id"],
        unique=True,
        postgresql_where=sa.text("status = 'open'"),
    )


def downgrade():
    op.drop_index("uq_character_reports_open_user_character", table_name="character_reports")
