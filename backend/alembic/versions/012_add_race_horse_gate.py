"""add gate column to race_horses

Revision ID: 012
Revises: 011
Create Date: 2026-07-01
"""

from alembic import op
import sqlalchemy as sa

revision = "012"
down_revision = "011"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("race_horses", sa.Column("gate", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("race_horses", "gate")
