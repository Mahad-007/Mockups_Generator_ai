"""Phase 9 canvas editor: add canvas_data to mockups."""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20241211_phase9_canvas_editor"
down_revision = "20241211_phase8_user_system"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add canvas_data to mockups
    with op.batch_alter_table("mockups") as batch_op:
        batch_op.add_column(sa.Column("canvas_data", sa.JSON(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("mockups") as batch_op:
        batch_op.drop_column("canvas_data")
