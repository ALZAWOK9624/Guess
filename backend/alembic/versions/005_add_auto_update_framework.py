"""add auto-update framework: manually_updated_fields + horse_auto_update_logs

Revision ID: 005
Revises: 004
Create Date: 2026-06-12
"""

from alembic import op
import sqlalchemy as sa

revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add manually_updated_fields column to horses table
    op.add_column(
        "horses",
        sa.Column("manually_updated_fields", sa.JSON(), nullable=True),
    )

    # Create horse_auto_update_logs table
    op.create_table(
        "horse_auto_update_logs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("horse_id", sa.Integer(), nullable=False),
        sa.Column("race_id", sa.Integer(), nullable=True),
        sa.Column("field_name", sa.String(length=100), nullable=False),
        sa.Column("old_value", sa.String(length=500), nullable=True),
        sa.Column("new_value", sa.String(length=500), nullable=True),
        sa.Column(
            "trigger_source",
            sa.String(length=50),
            nullable=False,
            server_default=sa.text("'settlement'"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["horse_id"], ["horses.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["race_id"], ["races.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_horse_auto_update_logs_horse_id"),
        "horse_auto_update_logs",
        ["horse_id"],
    )
    op.create_index(
        op.f("ix_horse_auto_update_logs_race_id"),
        "horse_auto_update_logs",
        ["race_id"],
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_horse_auto_update_logs_race_id"),
        table_name="horse_auto_update_logs",
    )
    op.drop_index(
        op.f("ix_horse_auto_update_logs_horse_id"),
        table_name="horse_auto_update_logs",
    )
    op.drop_table("horse_auto_update_logs")
    op.drop_column("horses", "manually_updated_fields")
