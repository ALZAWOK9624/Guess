"""add race_horses weight/jockey, remove horses weight/jockey

Revision ID: 009
Revises: 008
Create Date: 2026-06-16
"""

from alembic import op
import sqlalchemy as sa

revision = "009"
down_revision = "008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add weight and jockey columns to race_horses (per-race)
    op.add_column(
        "race_horses",
        sa.Column("weight", sa.String(20), nullable=True),
    )
    op.add_column(
        "race_horses",
        sa.Column("jockey", sa.String(50), nullable=True),
    )

    # Remove weight and jockey from horses (moved to per-race)
    op.drop_column("horses", "weight")
    op.drop_column("horses", "jockey")


def downgrade() -> None:
    # Restore weight and jockey on horses
    op.add_column(
        "horses",
        sa.Column("weight", sa.String(20), nullable=True),
    )
    op.add_column(
        "horses",
        sa.Column("jockey", sa.String(50), nullable=True),
    )

    # Remove columns from race_horses
    op.drop_column("race_horses", "weight")
    op.drop_column("race_horses", "jockey")
