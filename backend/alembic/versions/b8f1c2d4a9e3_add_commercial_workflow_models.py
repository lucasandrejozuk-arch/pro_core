"""add commercial workflow models

Revision ID: b8f1c2d4a9e3
Revises: 6a9d5c2f41e7
Create Date: 2026-05-14 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "b8f1c2d4a9e3"
down_revision: str | None = "6a9d5c2f41e7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


service_order_priority = postgresql.ENUM(
    "low",
    "normal",
    "high",
    "urgent",
    name="serviceorderpriority",
    create_type=False,
)
service_order_event_source = postgresql.ENUM(
    "staff",
    "customer",
    "system",
    name="serviceordereventsource",
    create_type=False,
)


def upgrade() -> None:
    bind = op.get_bind()
    for enum_type in (
        service_order_priority,
        service_order_event_source,
    ):
        enum_type.create(bind, checkfirst=True)

    op.add_column(
        "service_orders",
        sa.Column("priority", service_order_priority, nullable=True),
    )
    op.add_column(
        "service_orders",
        sa.Column("sla_due_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "service_orders",
        sa.Column("quote_sent_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "service_orders",
        sa.Column("approval_source", sa.String(length=40), nullable=True),
    )
    op.add_column(
        "service_orders",
        sa.Column("customer_decision_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "service_orders",
        sa.Column("customer_decision_name", sa.String(length=160), nullable=True),
    )
    op.execute("UPDATE service_orders SET priority = 'normal' WHERE priority IS NULL")
    op.alter_column("service_orders", "priority", nullable=False)
    op.create_index(op.f("ix_service_orders_priority"), "service_orders", ["priority"])
    op.create_index(op.f("ix_service_orders_sla_due_at"), "service_orders", ["sla_due_at"])

    op.create_table(
        "service_order_events",
        sa.Column("company_id", sa.Uuid(), nullable=False),
        sa.Column("service_order_id", sa.Uuid(), nullable=False),
        sa.Column("actor_user_id", sa.Uuid(), nullable=True),
        sa.Column("source", service_order_event_source, nullable=False),
        sa.Column("event_type", sa.String(length=80), nullable=False),
        sa.Column("message", sa.String(length=1000), nullable=False),
        sa.Column("metadata_json", sa.Text(), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["service_order_id"], ["service_orders.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_service_order_events_actor_user_id"), "service_order_events", ["actor_user_id"]
    )
    op.create_index(
        op.f("ix_service_order_events_company_id"), "service_order_events", ["company_id"]
    )
    op.create_index(
        op.f("ix_service_order_events_event_type"), "service_order_events", ["event_type"]
    )
    op.create_index(
        op.f("ix_service_order_events_service_order_id"),
        "service_order_events",
        ["service_order_id"],
    )
    op.create_index(op.f("ix_service_order_events_source"), "service_order_events", ["source"])

    op.create_table(
        "audit_logs",
        sa.Column("company_id", sa.Uuid(), nullable=False),
        sa.Column("actor_user_id", sa.Uuid(), nullable=True),
        sa.Column("actor_type", sa.String(length=40), nullable=False),
        sa.Column("action", sa.String(length=120), nullable=False),
        sa.Column("entity_type", sa.String(length=120), nullable=False),
        sa.Column("entity_id", sa.String(length=80), nullable=True),
        sa.Column("summary", sa.String(length=1000), nullable=False),
        sa.Column("metadata_json", sa.Text(), nullable=True),
        sa.Column("ip_address", sa.String(length=80), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_audit_logs_action"), "audit_logs", ["action"])
    op.create_index(op.f("ix_audit_logs_actor_user_id"), "audit_logs", ["actor_user_id"])
    op.create_index(op.f("ix_audit_logs_company_id"), "audit_logs", ["company_id"])
    op.create_index(op.f("ix_audit_logs_entity_id"), "audit_logs", ["entity_id"])
    op.create_index(op.f("ix_audit_logs_entity_type"), "audit_logs", ["entity_type"])


def downgrade() -> None:
    op.drop_index(op.f("ix_audit_logs_entity_type"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_entity_id"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_company_id"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_actor_user_id"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_action"), table_name="audit_logs")
    op.drop_table("audit_logs")

    op.drop_index(op.f("ix_service_order_events_source"), table_name="service_order_events")
    op.drop_index(
        op.f("ix_service_order_events_service_order_id"), table_name="service_order_events"
    )
    op.drop_index(op.f("ix_service_order_events_event_type"), table_name="service_order_events")
    op.drop_index(op.f("ix_service_order_events_company_id"), table_name="service_order_events")
    op.drop_index(op.f("ix_service_order_events_actor_user_id"), table_name="service_order_events")
    op.drop_table("service_order_events")

    op.drop_index(op.f("ix_service_orders_sla_due_at"), table_name="service_orders")
    op.drop_index(op.f("ix_service_orders_priority"), table_name="service_orders")
    op.drop_column("service_orders", "customer_decision_name")
    op.drop_column("service_orders", "customer_decision_at")
    op.drop_column("service_orders", "approval_source")
    op.drop_column("service_orders", "quote_sent_at")
    op.drop_column("service_orders", "sla_due_at")
    op.drop_column("service_orders", "priority")

    bind = op.get_bind()
    for enum_type in (
        service_order_event_source,
        service_order_priority,
    ):
        enum_type.drop(bind, checkfirst=True)
