"""create horses table

Revision ID: 003
Revises: 002
Create Date: 2026-06-11
"""

from alembic import op
import sqlalchemy as sa

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "horses",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("sex", sa.String(length=10), nullable=True),
        sa.Column("age", sa.Integer(), nullable=True),
        sa.Column("origin", sa.String(length=100), nullable=True),
        sa.Column("sire", sa.String(length=100), nullable=True),
        sa.Column("damsire", sa.String(length=100), nullable=True),
        sa.Column("weight", sa.String(length=20), nullable=True),
        sa.Column("jockey", sa.String(length=50), nullable=True),
        sa.Column("previous_result", sa.String(length=100), nullable=True),
        sa.Column("best_win", sa.String(length=100), nullable=True),
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
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_horses_name"), "horses", ["name"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_horses_name"), table_name="horses")
    op.drop_table("horses")
