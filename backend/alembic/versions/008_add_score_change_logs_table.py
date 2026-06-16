"""add score_change_logs table

Revision ID: 008
Revises: 007
Create Date: 2026-06-16
"""

from alembic import op
import sqlalchemy as sa

revision = "008"
down_revision = "007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "score_change_logs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("race_id", sa.Integer(), nullable=False),
        sa.Column("vote_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("admin_user_id", sa.Integer(), nullable=True),
        sa.Column("old_points", sa.Integer(), nullable=True),
        sa.Column("new_points", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["race_id"], ["races.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["vote_id"], ["votes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["admin_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_score_change_logs_race_id"),
        "score_change_logs",
        ["race_id"],
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_score_change_logs_race_id"), table_name="score_change_logs")
    op.drop_table("score_change_logs")
