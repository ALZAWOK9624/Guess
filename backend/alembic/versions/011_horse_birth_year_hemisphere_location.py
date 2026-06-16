"""horse: age→birth_year, add hemisphere, location

Revision ID: 011
Revises: 010
Create Date: 2026-06-16
"""

from alembic import op
import sqlalchemy as sa

revision = "011"
down_revision = "010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("horses", sa.Column("birth_year", sa.Integer(), nullable=True))
    op.add_column("horses", sa.Column("hemisphere", sa.String(10), nullable=True))
    op.add_column("horses", sa.Column("location", sa.String(100), nullable=True))
    op.drop_column("horses", "age")


def downgrade() -> None:
    op.add_column("horses", sa.Column("age", sa.Integer(), nullable=True))
    op.drop_column("horses", "location")
    op.drop_column("horses", "hemisphere")
    op.drop_column("horses", "birth_year")
