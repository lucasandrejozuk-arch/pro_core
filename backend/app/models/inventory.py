from __future__ import annotations

import uuid
from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base
from backend.app.models.common import ModelBase


class InventoryItem(ModelBase, Base):
    __tablename__ = "inventory_items"
    __table_args__ = (UniqueConstraint("company_id", "sku", name="uq_inventory_company_sku"),)

    company_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    sku: Mapped[str | None] = mapped_column(String(80), nullable=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    category: Mapped[str | None] = mapped_column(String(80), nullable=True)
    quantity: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    minimum_quantity: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    unit_cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)

    company: Mapped["Company"] = relationship(back_populates="inventory_items")
    budget_items: Mapped[list["ServiceOrderBudgetItem"]] = relationship(
        back_populates="inventory_item"
    )

