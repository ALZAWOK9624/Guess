"""add race tag fields, drop grade enum

Revision ID: 014
Revises: 013
Create Date: 2026-07-07
"""

from alembic import op
import sqlalchemy as sa


revision = "014"
down_revision = "013"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new race tag columns
    op.add_column("races", sa.Column("age_range", sa.String(20), nullable=False, server_default="其他"))
    op.add_column("races", sa.Column("sex_restriction", sa.String(20), nullable=False, server_default="无"))
    op.add_column("races", sa.Column("race_grade", sa.String(20), nullable=False, server_default="G1"))
    op.add_column("races", sa.Column("country", sa.String(50), nullable=False, server_default="日本"))
    op.add_column("races", sa.Column("distance", sa.String(50), nullable=False, server_default=""))

    # Migrate existing data: map old grade values to new race_grade
    # G1 → G1, G2_JPN1 → G2 (conservative mapping), YOUNG_G1 → G1, CUSTOM → 自定义
    op.execute("""
        UPDATE races
        SET race_grade = CASE
            WHEN grade::text = 'G1' THEN 'G1'
            WHEN grade::text = 'G2_JPN1' THEN 'G2'
            WHEN grade::text = 'YOUNG_G1' THEN 'G1'
            WHEN grade::text = 'CUSTOM' THEN '自定义'
            ELSE '其他'
        END,
        age_range = CASE
            WHEN grade::text = 'YOUNG_G1' THEN '2岁'
            ELSE '其他'
        END
    """)

    # Drop server_default on new columns (after migration)
    op.alter_column("races", "age_range", server_default=None)
    op.alter_column("races", "sex_restriction", server_default=None)
    op.alter_column("races", "race_grade", server_default=None)
    op.alter_column("races", "country", server_default=None)
    op.alter_column("races", "distance", server_default=None)

    # Drop the old grade column
    op.drop_column("races", "grade")

    # Drop the grade_enum type
    op.execute("DROP TYPE IF EXISTS grade_enum")


def downgrade() -> None:
    # Re-create grade_enum type
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'grade_enum') THEN
            CREATE TYPE grade_enum AS ENUM ('G1', 'G2_JPN1', 'YOUNG_G1', 'CUSTOM');
        END IF;
    END
    $$;
    """)

    # Re-add grade column as the enum type
    op.add_column(
        "races",
        sa.Column(
            "grade",
            sa.Enum("G1", "G2_JPN1", "YOUNG_G1", "CUSTOM", name="grade_enum", create_type=False),
            nullable=True,
        ),
    )

    # Attempt to reverse-migrate data
    op.execute("""
        UPDATE races
        SET grade = CASE
            WHEN race_grade = 'G1' THEN 'G1'::grade_enum
            WHEN race_grade = '自定义' THEN 'CUSTOM'::grade_enum
            ELSE 'G1'::grade_enum
        END
    """)

    op.alter_column("races", "grade", nullable=False)

    # Drop new columns
    op.drop_column("races", "distance")
    op.drop_column("races", "country")
    op.drop_column("races", "race_grade")
    op.drop_column("races", "sex_restriction")
    op.drop_column("races", "age_range")
