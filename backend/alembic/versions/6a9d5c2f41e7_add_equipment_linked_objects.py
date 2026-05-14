"""add equipment linked objects

Revision ID: 6a9d5c2f41e7
Revises: f3d8a2c5e9b1
Create Date: 2026-05-14 00:00:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "6a9d5c2f41e7"
down_revision: str | None = "f3d8a2c5e9b1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "equipment",
        sa.Column("special_number", sa.String(length=120), nullable=True),
    )
    op.create_index(
        op.f("ix_equipment_special_number"),
        "equipment",
        ["special_number"],
        unique=False,
    )

    op.create_table(
        "equipment_boards",
        sa.Column("company_id", sa.Uuid(), nullable=False),
        sa.Column("equipment_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("special_number", sa.String(length=120), nullable=True),
        sa.Column("serial_number", sa.String(length=120), nullable=True),
        sa.Column("model", sa.String(length=120), nullable=True),
        sa.Column("revision", sa.String(length=80), nullable=True),
        sa.Column("notes", sa.String(length=1000), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["equipment_id"], ["equipment.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_equipment_boards_company_id"),
        "equipment_boards",
        ["company_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_equipment_boards_equipment_id"),
        "equipment_boards",
        ["equipment_id"],
        unique=False,
    )

    op.create_table(
        "equipment_board_components",
        sa.Column("company_id", sa.Uuid(), nullable=False),
        sa.Column("board_id", sa.Uuid(), nullable=False),
        sa.Column("category", sa.String(length=120), nullable=True),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("quantity", sa.String(length=40), nullable=True),
        sa.Column("part_number", sa.String(length=120), nullable=True),
        sa.Column("location", sa.String(length=120), nullable=True),
        sa.Column("notes", sa.String(length=1000), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["board_id"], ["equipment_boards.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_equipment_board_components_board_id"),
        "equipment_board_components",
        ["board_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_equipment_board_components_company_id"),
        "equipment_board_components",
        ["company_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_equipment_board_components_company_id"),
        table_name="equipment_board_components",
    )
    op.drop_index(
        op.f("ix_equipment_board_components_board_id"),
        table_name="equipment_board_components",
    )
    op.drop_table("equipment_board_components")

    op.drop_index(op.f("ix_equipment_boards_equipment_id"), table_name="equipment_boards")
    op.drop_index(op.f("ix_equipment_boards_company_id"), table_name="equipment_boards")
    op.drop_table("equipment_boards")

    op.drop_index(op.f("ix_equipment_special_number"), table_name="equipment")
    op.drop_column("equipment", "special_number")
