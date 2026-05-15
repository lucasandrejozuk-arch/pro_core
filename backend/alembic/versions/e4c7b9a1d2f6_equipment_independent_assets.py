"""equipment independent assets

Revision ID: e4c7b9a1d2f6
Revises: b8f1c2d4a9e3
Create Date: 2026-05-15 00:00:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "e4c7b9a1d2f6"
down_revision: str | None = "b8f1c2d4a9e3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "equipment",
        sa.Column(
            "unit_price",
            sa.Numeric(precision=12, scale=2),
            server_default="0",
            nullable=False,
        ),
    )
    op.add_column(
        "equipment_boards",
        sa.Column(
            "unit_price",
            sa.Numeric(precision=12, scale=2),
            server_default="0",
            nullable=False,
        ),
    )
    op.add_column(
        "equipment_board_components",
        sa.Column(
            "unit_price",
            sa.Numeric(precision=12, scale=2),
            server_default="0",
            nullable=False,
        ),
    )

    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.drop_constraint("equipment_customer_id_fkey", "equipment", type_="foreignkey")
        op.create_foreign_key(
            "equipment_customer_id_fkey",
            "equipment",
            "customers",
            ["customer_id"],
            ["id"],
            ondelete="SET NULL",
        )
        op.alter_column("equipment", "customer_id", existing_type=sa.Uuid(), nullable=True)
    else:
        with op.batch_alter_table("equipment") as batch_op:
            batch_op.alter_column("customer_id", existing_type=sa.Uuid(), nullable=True)


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.drop_constraint("equipment_customer_id_fkey", "equipment", type_="foreignkey")
        op.create_foreign_key(
            "equipment_customer_id_fkey",
            "equipment",
            "customers",
            ["customer_id"],
            ["id"],
            ondelete="CASCADE",
        )
        op.alter_column("equipment", "customer_id", existing_type=sa.Uuid(), nullable=False)
    else:
        with op.batch_alter_table("equipment") as batch_op:
            batch_op.alter_column("customer_id", existing_type=sa.Uuid(), nullable=False)

    op.drop_column("equipment_board_components", "unit_price")
    op.drop_column("equipment_boards", "unit_price")
    op.drop_column("equipment", "unit_price")
