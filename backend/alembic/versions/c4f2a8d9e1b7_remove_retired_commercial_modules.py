"""remove retired commercial modules

Revision ID: c4f2a8d9e1b7
Revises: 9a7e3c5b1d20
Create Date: 2026-05-20 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "c4f2a8d9e1b7"
down_revision: str | None = "9a7e3c5b1d20"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

financial_record_type = postgresql.ENUM(
    "receivable",
    "payable",
    name="financialrecordtype",
    create_type=False,
)
financial_record_status = postgresql.ENUM(
    "open",
    "paid",
    "canceled",
    "overdue",
    name="financialrecordstatus",
    create_type=False,
)
notification_channel = postgresql.ENUM(
    "email",
    "whatsapp",
    "system",
    name="notificationchannel",
    create_type=False,
)
notification_status = postgresql.ENUM(
    "pending",
    "sent",
    "failed",
    name="notificationstatus",
    create_type=False,
)


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    for table_name in ("notification_logs", "financial_records"):
        if inspector.has_table(table_name):
            op.drop_table(table_name)

    for table_name in ("equipment", "equipment_boards", "equipment_board_components"):
        op.alter_column(
            table_name,
            "unit_price",
            existing_type=sa.Numeric(precision=12, scale=2),
            server_default=None,
            existing_nullable=False,
        )

    if bind.dialect.name == "postgresql":
        for type_name in (
            "notificationstatus",
            "notificationchannel",
            "financialrecordstatus",
            "financialrecordtype",
        ):
            op.execute(sa.text(f"DROP TYPE IF EXISTS {type_name}"))


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    for table_name in ("equipment", "equipment_boards", "equipment_board_components"):
        op.alter_column(
            table_name,
            "unit_price",
            existing_type=sa.Numeric(precision=12, scale=2),
            server_default=sa.text("0"),
            existing_nullable=False,
        )

    for enum_type in (
        financial_record_type,
        financial_record_status,
        notification_channel,
        notification_status,
    ):
        enum_type.create(bind, checkfirst=True)

    if not inspector.has_table("financial_records"):
        op.create_table(
            "financial_records",
            sa.Column("company_id", sa.Uuid(), nullable=False),
            sa.Column("service_order_id", sa.Uuid(), nullable=True),
            sa.Column("record_type", financial_record_type, nullable=False),
            sa.Column("status", financial_record_status, nullable=False),
            sa.Column("description", sa.String(length=240), nullable=False),
            sa.Column("amount", sa.Numeric(precision=12, scale=2), nullable=False),
            sa.Column("due_date", sa.Date(), nullable=True),
            sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("id", sa.Uuid(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
            sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(
                ["service_order_id"],
                ["service_orders.id"],
                ondelete="SET NULL",
            ),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(
            op.f("ix_financial_records_company_id"),
            "financial_records",
            ["company_id"],
        )
        op.create_index(
            op.f("ix_financial_records_due_date"),
            "financial_records",
            ["due_date"],
        )
        op.create_index(
            op.f("ix_financial_records_record_type"),
            "financial_records",
            ["record_type"],
        )
        op.create_index(
            op.f("ix_financial_records_service_order_id"),
            "financial_records",
            ["service_order_id"],
        )
        op.create_index(
            op.f("ix_financial_records_status"),
            "financial_records",
            ["status"],
        )

    if not inspector.has_table("notification_logs"):
        op.create_table(
            "notification_logs",
            sa.Column("company_id", sa.Uuid(), nullable=False),
            sa.Column("service_order_id", sa.Uuid(), nullable=True),
            sa.Column("channel", notification_channel, nullable=False),
            sa.Column("status", notification_status, nullable=False),
            sa.Column("recipient", sa.String(length=255), nullable=False),
            sa.Column("subject", sa.String(length=240), nullable=True),
            sa.Column("message", sa.Text(), nullable=False),
            sa.Column("provider_response", sa.Text(), nullable=True),
            sa.Column("id", sa.Uuid(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
            sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(
                ["service_order_id"],
                ["service_orders.id"],
                ondelete="SET NULL",
            ),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(
            op.f("ix_notification_logs_channel"),
            "notification_logs",
            ["channel"],
        )
        op.create_index(
            op.f("ix_notification_logs_company_id"),
            "notification_logs",
            ["company_id"],
        )
        op.create_index(
            op.f("ix_notification_logs_service_order_id"),
            "notification_logs",
            ["service_order_id"],
        )
        op.create_index(
            op.f("ix_notification_logs_status"),
            "notification_logs",
            ["status"],
        )
