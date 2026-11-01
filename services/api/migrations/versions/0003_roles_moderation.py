"""Add RBAC and character moderation state."""
from alembic import op
import sqlalchemy as sa
revision = "0003_roles_moderation"
down_revision = "0002_conversations"
branch_labels = None
depends_on = None

def upgrade():
    op.add_column("users", sa.Column("role", sa.String(20), nullable=False, server_default="user"))
    op.add_column("characters", sa.Column("moderation_status", sa.String(16), nullable=False, server_default="pending"))
    op.add_column("characters", sa.Column("moderation_note", sa.Text(), nullable=True))
    op.create_index("ix_characters_moderation_status", "characters", ["moderation_status"])

def downgrade():
    op.drop_index("ix_characters_moderation_status", table_name="characters")
    op.drop_column("characters", "moderation_note")
    op.drop_column("characters", "moderation_status")
    op.drop_column("users", "role")
