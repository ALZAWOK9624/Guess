"""add surface column to races

Revision ID: 015
Revises: 014
Create Date: 2026-07-07
"""

from alembic import op
import sqlalchemy as sa


revision = "015"
down_revision = "014"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("races", sa.Column("surface", sa.String(20), nullable=False, server_default="草地"))

    # Remove server_default after existing rows are populated
    op.alter_column("races", "surface", server_default=None)


def downgrade() -> None:
    op.drop_column("races", "surface")
