"""inventory assistant upgrade

Revision ID: d1b7f4c2a8e6
Revises: c4f2a8d9e1b7
Create Date: 2026-05-21 00:00:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "d1b7f4c2a8e6"
down_revision: str | None = "c4f2a8d9e1b7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "inventory_items",
        sa.Column("stock_group", sa.String(length=32), server_default="components", nullable=False),
    )
    op.add_column("inventory_items", sa.Column("location", sa.String(length=120), nullable=True))
    op.add_column("inventory_items", sa.Column("notes", sa.Text(), nullable=True))
    op.add_column("inventory_items", sa.Column("technical_data_json", sa.Text(), nullable=True))

    op.add_column(
        "document_attachments",
        sa.Column("inventory_item_id", sa.Uuid(), nullable=True),
    )
    op.create_index(
        op.f("ix_document_attachments_inventory_item_id"),
        "document_attachments",
        ["inventory_item_id"],
        unique=False,
    )

    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.create_foreign_key(
            "document_attachments_inventory_item_id_fkey",
            "document_attachments",
            "inventory_items",
            ["inventory_item_id"],
            ["id"],
            ondelete="CASCADE",
        )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.drop_constraint(
            "document_attachments_inventory_item_id_fkey",
            "document_attachments",
            type_="foreignkey",
        )

    op.drop_index(
        op.f("ix_document_attachments_inventory_item_id"),
        table_name="document_attachments",
    )
    op.drop_column("document_attachments", "inventory_item_id")

    op.drop_column("inventory_items", "technical_data_json")
    op.drop_column("inventory_items", "notes")
    op.drop_column("inventory_items", "location")
    op.drop_column("inventory_items", "stock_group")
