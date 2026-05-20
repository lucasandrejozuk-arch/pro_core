"""add equipment defect cases

Revision ID: 2d9f0c8b7a61
Revises: e4c7b9a1d2f6
Create Date: 2026-05-15 00:00:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "2d9f0c8b7a61"
down_revision: str | None = "e4c7b9a1d2f6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "equipment_defect_cases",
        sa.Column("company_id", sa.Uuid(), nullable=False),
        sa.Column("equipment_id", sa.Uuid(), nullable=False),
        sa.Column("board_id", sa.Uuid(), nullable=True),
        sa.Column("title", sa.String(length=160), nullable=False),
        sa.Column("symptom", sa.String(length=2000), nullable=True),
        sa.Column("root_cause", sa.String(length=2000), nullable=True),
        sa.Column("solution", sa.String(length=2000), nullable=True),
        sa.Column("notes", sa.String(length=2000), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["board_id"], ["equipment_boards.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["equipment_id"], ["equipment.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_equipment_defect_cases_board_id"),
        "equipment_defect_cases",
        ["board_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_equipment_defect_cases_company_id"),
        "equipment_defect_cases",
        ["company_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_equipment_defect_cases_equipment_id"),
        "equipment_defect_cases",
        ["equipment_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_equipment_defect_cases_equipment_id"), table_name="equipment_defect_cases")
    op.drop_index(op.f("ix_equipment_defect_cases_company_id"), table_name="equipment_defect_cases")
    op.drop_index(op.f("ix_equipment_defect_cases_board_id"), table_name="equipment_defect_cases")
    op.drop_table("equipment_defect_cases")
