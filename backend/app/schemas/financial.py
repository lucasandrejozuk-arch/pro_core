from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from backend.app.models.enums import FinancialRecordStatus, FinancialRecordType


class FinancialRecordCreate(BaseModel):
    service_order_id: uuid.UUID | None = None
    record_type: FinancialRecordType = FinancialRecordType.RECEIVABLE
    description: str = Field(min_length=1, max_length=240)
    amount: Decimal = Field(gt=0)
    due_date: date | None = None
    notes: str | None = None


class FinancialRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_id: uuid.UUID
    service_order_id: uuid.UUID | None
    record_type: FinancialRecordType
    status: FinancialRecordStatus
    description: str
    amount: Decimal
    due_date: date | None
    paid_at: datetime | None
    notes: str | None
    created_at: datetime
    updated_at: datetime
