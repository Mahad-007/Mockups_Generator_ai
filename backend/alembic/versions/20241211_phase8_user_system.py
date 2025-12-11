"""Phase 8 user system scaffolding: user fields, teams, ownership."""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20241211_phase8_user_system"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Users: add usage + tokens + verification flags
    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(sa.Column("usage_counts", sa.JSON(), nullable=True, server_default="{}"))
        batch_op.add_column(sa.Column("usage_reset_at", sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column("email_verified", sa.Boolean(), nullable=False, server_default=sa.false()))
        batch_op.add_column(sa.Column("verify_token", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("reset_token", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("reset_token_expires_at", sa.DateTime(), nullable=True))

    # Products: owner
    with op.batch_alter_table("products") as batch_op:
        batch_op.add_column(sa.Column("user_id", sa.String(), nullable=True))
        batch_op.create_foreign_key("products_user_id_fkey", "users", ["user_id"], ["id"])

    # Mockups: owner
    with op.batch_alter_table("mockups") as batch_op:
        batch_op.add_column(sa.Column("user_id", sa.String(), nullable=True))
        batch_op.create_foreign_key("mockups_user_id_fkey", "users", ["user_id"], ["id"])

    # Teams
    op.create_table(
        "teams",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("owner_id", sa.String(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    op.create_table(
        "team_memberships",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("team_id", sa.String(), sa.ForeignKey("teams.id"), nullable=False),
        sa.Column("user_id", sa.String(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column(
            "role",
            sa.Enum("owner", "admin", "member", name="membershiprole"),
            nullable=False,
            server_default="member",
        ),
        sa.Column("invited_email", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("team_memberships")
    op.drop_table("teams")

    with op.batch_alter_table("mockups") as batch_op:
        batch_op.drop_constraint("mockups_user_id_fkey", type_="foreignkey")
        batch_op.drop_column("user_id")

    with op.batch_alter_table("products") as batch_op:
        batch_op.drop_constraint("products_user_id_fkey", type_="foreignkey")
        batch_op.drop_column("user_id")

    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_column("reset_token_expires_at")
        batch_op.drop_column("reset_token")
        batch_op.drop_column("verify_token")
        batch_op.drop_column("email_verified")
        batch_op.drop_column("usage_reset_at")
        batch_op.drop_column("usage_counts")

