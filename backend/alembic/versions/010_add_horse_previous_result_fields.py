"""add previous_result_date, previous_result_position, best_win_date to horses

Revision ID: 010
Revises: 009
Create Date: 2026-06-16
"""

from alembic import op
import sqlalchemy as sa

revision = "010"
down_revision = "009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "horses",
        sa.Column("previous_result_date", sa.Date(), nullable=True),
    )
    op.add_column(
        "horses",
        sa.Column("previous_result_position", sa.Integer(), nullable=True),
    )
    op.add_column(
        "horses",
        sa.Column("best_win_date", sa.Date(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("horses", "best_win_date")
    op.drop_column("horses", "previous_result_position")
    op.drop_column("horses", "previous_result_date")
