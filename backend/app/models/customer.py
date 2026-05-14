from __future__ import annotations

import uuid

from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base
from backend.app.models.common import ModelBase


class Customer(ModelBase, Base):
    __tablename__ = "customers"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uq_customers_company_document"),
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    document_number: Mapped[str | None] = mapped_column(String(32), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    company: Mapped["Company"] = relationship(back_populates="customers")
    equipment: Mapped[list["Equipment"]] = relationship(back_populates="customer")
    service_orders: Mapped[list["ServiceOrder"]] = relationship(back_populates="customer")
    documents: Mapped[list["DocumentAttachment"]] = relationship(back_populates="customer")

