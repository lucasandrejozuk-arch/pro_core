from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base
from backend.app.models.common import ModelBase


class Equipment(ModelBase, Base):
    __tablename__ = "equipment"

    company_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    customer_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    category: Mapped[str] = mapped_column(String(80), nullable=False)
    brand: Mapped[str | None] = mapped_column(String(80), nullable=True)
    model: Mapped[str | None] = mapped_column(String(120), nullable=True)
    serial_number: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    company: Mapped["Company"] = relationship(back_populates="equipment")
    customer: Mapped["Customer"] = relationship(back_populates="equipment")
    service_orders: Mapped[list["ServiceOrder"]] = relationship(back_populates="equipment")
    documents: Mapped[list["DocumentAttachment"]] = relationship(back_populates="equipment")

