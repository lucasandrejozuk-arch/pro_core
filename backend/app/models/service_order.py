from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String, Text, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base
from backend.app.models.common import ModelBase
from backend.app.models.enums import (
    BudgetItemType,
    ServiceOrderEventSource,
    ServiceOrderPriority,
    ServiceOrderStatus,
    enum_values,
)


class ServiceOrder(ModelBase, Base):
    __tablename__ = "service_orders"
    __table_args__ = (UniqueConstraint("company_id", "code", name="uq_service_orders_company_code"),)

    company_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    customer_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("customers.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    equipment_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("equipment.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    assigned_technician_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    code: Mapped[str] = mapped_column(String(40), nullable=False)
    status: Mapped[ServiceOrderStatus] = mapped_column(
        Enum(ServiceOrderStatus, values_callable=enum_values),
        default=ServiceOrderStatus.OPEN,
        nullable=False,
        index=True,
    )
    priority: Mapped[ServiceOrderPriority] = mapped_column(
        Enum(ServiceOrderPriority, values_callable=enum_values),
        default=ServiceOrderPriority.NORMAL,
        nullable=False,
        index=True,
    )
    problem_description: Mapped[str] = mapped_column(String(2000), nullable=False)
    technical_diagnosis: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    rejection_reason: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    quoted_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    sla_due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    quote_sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    approval_source: Mapped[str | None] = mapped_column(String(40), nullable=True)
    customer_decision_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    customer_decision_name: Mapped[str | None] = mapped_column(String(160), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    company: Mapped["Company"] = relationship(back_populates="service_orders")
    customer: Mapped["Customer"] = relationship(back_populates="service_orders")
    equipment: Mapped["Equipment"] = relationship(back_populates="service_orders")
    assigned_technician: Mapped["User | None"] = relationship(
        back_populates="assigned_service_orders",
        foreign_keys=[assigned_technician_id],
    )
    budget_items: Mapped[list["ServiceOrderBudgetItem"]] = relationship(
        back_populates="service_order",
        cascade="all, delete-orphan",
    )
    events: Mapped[list["ServiceOrderEvent"]] = relationship(
        back_populates="service_order",
        cascade="all, delete-orphan",
        order_by="ServiceOrderEvent.created_at",
    )
    documents: Mapped[list["DocumentAttachment"]] = relationship(back_populates="service_order")


class ServiceOrderBudgetItem(ModelBase, Base):
    __tablename__ = "service_order_budget_items"

    service_order_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("service_orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    inventory_item_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("inventory_items.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    item_type: Mapped[BudgetItemType] = mapped_column(
        Enum(BudgetItemType, values_callable=enum_values),
        default=BudgetItemType.SERVICE,
        nullable=False,
    )
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=1, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)

    service_order: Mapped["ServiceOrder"] = relationship(back_populates="budget_items")
    inventory_item: Mapped["InventoryItem | None"] = relationship(back_populates="budget_items")


class ServiceOrderEvent(ModelBase, Base):
    __tablename__ = "service_order_events"

    company_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    service_order_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("service_orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    actor_user_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    source: Mapped[ServiceOrderEventSource] = mapped_column(
        Enum(ServiceOrderEventSource, values_callable=enum_values),
        default=ServiceOrderEventSource.STAFF,
        nullable=False,
        index=True,
    )
    event_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    message: Mapped[str] = mapped_column(String(1000), nullable=False)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    service_order: Mapped["ServiceOrder"] = relationship(back_populates="events")
    actor_user: Mapped["User | None"] = relationship(foreign_keys=[actor_user_id])
