from __future__ import annotations

import json
import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Numeric, String, Text, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base
from backend.app.models.common import ModelBase

if TYPE_CHECKING:
    from backend.app.models.company import Company
    from backend.app.models.document import DocumentAttachment
    from backend.app.models.service_order import ServiceOrderBudgetItem


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
    stock_group: Mapped[str] = mapped_column(String(32), default="components", nullable=False)
    location: Mapped[str | None] = mapped_column(String(120), nullable=True)
    quantity: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    minimum_quantity: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    unit_cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    technical_data_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    company: Mapped[Company] = relationship(back_populates="inventory_items")
    budget_items: Mapped[list[ServiceOrderBudgetItem]] = relationship(
        back_populates="inventory_item"
    )
    documents: Mapped[list[DocumentAttachment]] = relationship(back_populates="inventory_item")

    @property
    def technical_data(self) -> dict[str, str] | None:
        raw_value = self.technical_data_json
        if not raw_value:
            return None
        try:
            parsed = json.loads(raw_value)
        except (TypeError, ValueError):
            return None
        if not isinstance(parsed, dict):
            return None
        return {str(key): str(value) for key, value in parsed.items() if value is not None}

    @technical_data.setter
    def technical_data(self, value: dict[str, str] | None) -> None:
        if not value:
            self.technical_data_json = None
            return
        normalized = {
            str(key): str(field_value)
            for key, field_value in value.items()
            if str(key).strip() and field_value is not None and str(field_value).strip()
        }
        self.technical_data_json = json.dumps(normalized, ensure_ascii=True) if normalized else None
