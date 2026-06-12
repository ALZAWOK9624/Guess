"""create votes table

Revision ID: 006
Revises: 005
Create Date: 2026-06-12
"""

from alembic import op
import sqlalchemy as sa

revision = "006"
down_revision = "005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "votes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("race_id", sa.Integer(), nullable=False),
        sa.Column("race_horse_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["race_id"], ["races.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["race_horse_id"], ["race_horses.id"]
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "race_id", name="uq_vote_user_race"),
    )
    op.create_index(
        op.f("ix_votes_race_id"), "votes", ["race_id"]
    )
    op.create_index(
        op.f("ix_votes_user_id"), "votes", ["user_id"]
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_votes_user_id"), table_name="votes")
    op.drop_index(op.f("ix_votes_race_id"), table_name="votes")
    op.drop_table("votes")
