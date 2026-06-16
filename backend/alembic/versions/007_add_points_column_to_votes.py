"""add points column to votes

Revision ID: 007
Revises: 006
Create Date: 2026-06-16
"""

from alembic import op
import sqlalchemy as sa

revision = "007"
down_revision = "006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "votes",
        sa.Column("points", sa.Integer(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("votes", "points")
