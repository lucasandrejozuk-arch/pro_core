from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Numeric, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base
from backend.app.models.common import ModelBase
from backend.app.models.enums import FinancialRecordStatus, FinancialRecordType, enum_values


class FinancialRecord(ModelBase, Base):
    __tablename__ = "financial_records"

    company_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    service_order_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("service_orders.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    record_type: Mapped[FinancialRecordType] = mapped_column(
        Enum(FinancialRecordType, values_callable=enum_values),
        default=FinancialRecordType.RECEIVABLE,
        nullable=False,
        index=True,
    )
    status: Mapped[FinancialRecordStatus] = mapped_column(
        Enum(FinancialRecordStatus, values_callable=enum_values),
        default=FinancialRecordStatus.OPEN,
        nullable=False,
        index=True,
    )
    description: Mapped[str] = mapped_column(String(240), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    service_order: Mapped["ServiceOrder | None"] = relationship()
