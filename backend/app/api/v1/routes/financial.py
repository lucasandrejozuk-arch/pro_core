from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.api.dependencies import require_roles
from backend.app.db.session import get_db
from backend.app.models.enums import FinancialRecordStatus, UserRole
from backend.app.models.financial import FinancialRecord
from backend.app.models.user import User
from backend.app.schemas.financial import FinancialRecordCreate, FinancialRecordResponse
from backend.app.services.audit import create_audit_log
from backend.app.services.financial import (
    cancel_financial_record,
    create_financial_record,
    delete_financial_record,
    list_financial_records,
    mark_financial_record_paid,
)

router = APIRouter(prefix="/financial-records", tags=["financial-records"])
admin_or_manager = require_roles(UserRole.ADMIN, UserRole.MANAGER)


@router.get("", response_model=list[FinancialRecordResponse])
def list_financial_record_items(
    status_filter: FinancialRecordStatus | None = Query(default=None, alias="status"),
    current_user: User = Depends(admin_or_manager),
    db: Session = Depends(get_db),
) -> list[FinancialRecordResponse]:
    return list_financial_records(db, current_user.company_id, status_filter)


@router.post("", response_model=FinancialRecordResponse, status_code=status.HTTP_201_CREATED)
def create_financial_record_item(
    payload: FinancialRecordCreate,
    current_user: User = Depends(admin_or_manager),
    db: Session = Depends(get_db),
) -> FinancialRecordResponse:
    record = create_financial_record(
        db=db,
        company_id=current_user.company_id,
        record_type=payload.record_type,
        description=payload.description,
        amount=payload.amount,
        service_order_id=payload.service_order_id,
        due_date=payload.due_date,
        notes=payload.notes,
    )
    create_audit_log(
        db,
        company_id=current_user.company_id,
        actor_user_id=current_user.id,
        action="financial_record.created",
        entity_type="financial_record",
        entity_id=record.id,
        summary=f"Lancamento financeiro criado: {record.description}.",
    )
    db.commit()
    db.refresh(record)
    return record


@router.post("/{record_id}/mark-paid", response_model=FinancialRecordResponse)
def mark_financial_record_paid_item(
    record_id: uuid.UUID,
    current_user: User = Depends(admin_or_manager),
    db: Session = Depends(get_db),
) -> FinancialRecordResponse:
    record = _get_financial_record(db, current_user.company_id, record_id)
    return mark_financial_record_paid(db, record)


@router.post("/{record_id}/cancel", response_model=FinancialRecordResponse)
def cancel_financial_record_item(
    record_id: uuid.UUID,
    current_user: User = Depends(admin_or_manager),
    db: Session = Depends(get_db),
) -> FinancialRecordResponse:
    record = _get_financial_record(db, current_user.company_id, record_id)
    return cancel_financial_record(db, record)


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_financial_record_item(
    record_id: uuid.UUID,
    current_user: User = Depends(admin_or_manager),
    db: Session = Depends(get_db),
) -> None:
    record = _get_financial_record(db, current_user.company_id, record_id)
    delete_financial_record(db, record)


def _get_financial_record(
    db: Session,
    company_id: uuid.UUID,
    record_id: uuid.UUID,
) -> FinancialRecord:
    record = db.get(FinancialRecord, record_id)
    if record is None or record.company_id != company_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Financial record not found.")
    return record
