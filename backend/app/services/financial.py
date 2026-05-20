from __future__ import annotations

import uuid
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.enums import FinancialRecordStatus, FinancialRecordType
from backend.app.models.financial import FinancialRecord
from backend.app.models.service_order import ServiceOrder


def list_financial_records(
    db: Session,
    company_id: uuid.UUID,
    status: FinancialRecordStatus | None = None,
) -> list[FinancialRecord]:
    statement = (
        select(FinancialRecord)
        .where(FinancialRecord.company_id == company_id)
        .order_by(FinancialRecord.created_at.desc())
    )
    if status is not None:
        statement = statement.where(FinancialRecord.status == status)
    return list(db.scalars(statement))


def create_financial_record(
    db: Session,
    company_id: uuid.UUID,
    record_type: FinancialRecordType,
    description: str,
    amount: Decimal,
    service_order_id: uuid.UUID | None = None,
    due_date: date | None = None,
    notes: str | None = None,
) -> FinancialRecord:
    record = FinancialRecord(
        company_id=company_id,
        service_order_id=service_order_id,
        record_type=record_type,
        status=FinancialRecordStatus.OPEN,
        description=description,
        amount=amount,
        due_date=due_date,
        notes=notes,
    )
    db.add(record)
    return record


def create_receivable_for_service_order(
    db: Session,
    service_order: ServiceOrder,
) -> FinancialRecord | None:
    if service_order.quoted_total <= Decimal("0"):
        return None

    existing = db.scalars(
        select(FinancialRecord).where(
            FinancialRecord.company_id == service_order.company_id,
            FinancialRecord.service_order_id == service_order.id,
            FinancialRecord.record_type == FinancialRecordType.RECEIVABLE,
            FinancialRecord.status != FinancialRecordStatus.CANCELED,
        )
    ).first()
    if existing is not None:
        existing.amount = service_order.quoted_total
        existing.description = f"Recebimento da {service_order.code}"
        db.add(existing)
        return existing

    due_date = datetime.now(UTC).date() + timedelta(days=7)
    return create_financial_record(
        db=db,
        company_id=service_order.company_id,
        service_order_id=service_order.id,
        record_type=FinancialRecordType.RECEIVABLE,
        description=f"Recebimento da {service_order.code}",
        amount=service_order.quoted_total,
        due_date=due_date,
        notes="Gerado automaticamente na aprovacao do orcamento.",
    )


def mark_financial_record_paid(db: Session, record: FinancialRecord) -> FinancialRecord:
    record.status = FinancialRecordStatus.PAID
    record.paid_at = datetime.now(UTC)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def cancel_financial_record(db: Session, record: FinancialRecord) -> FinancialRecord:
    record.status = FinancialRecordStatus.CANCELED
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def delete_financial_record(db: Session, record: FinancialRecord) -> None:
    db.delete(record)
    db.commit()
