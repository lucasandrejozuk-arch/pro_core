from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from backend.app.models.enums import BudgetItemType, ServiceOrderStatus


class ServiceOrderCreate(BaseModel):
    customer_id: uuid.UUID
    equipment_id: uuid.UUID
    assigned_technician_id: uuid.UUID | None = None
    problem_description: str = Field(min_length=1, max_length=2000)


class ServiceOrderUpdate(BaseModel):
    assigned_technician_id: uuid.UUID | None = None
    problem_description: str | None = Field(default=None, min_length=1, max_length=2000)
    technical_diagnosis: str | None = Field(default=None, max_length=2000)
    rejection_reason: str | None = Field(default=None, max_length=1000)


class DiagnosisRequest(BaseModel):
    technical_diagnosis: str = Field(min_length=1, max_length=2000)


class RejectServiceOrderRequest(BaseModel):
    rejection_reason: str = Field(min_length=1, max_length=1000)


class BudgetItemCreate(BaseModel):
    inventory_item_id: uuid.UUID | None = None
    item_type: BudgetItemType = BudgetItemType.SERVICE
    description: str = Field(min_length=1, max_length=500)
    quantity: Decimal = Field(default=Decimal("1"), gt=0)
    unit_price: Decimal = Field(default=Decimal("0"), ge=0)


class BudgetItemResponse(BudgetItemCreate):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    service_order_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class ServiceOrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_id: uuid.UUID
    customer_id: uuid.UUID
    equipment_id: uuid.UUID
    assigned_technician_id: uuid.UUID | None
    code: str
    status: ServiceOrderStatus
    problem_description: str
    technical_diagnosis: str | None
    rejection_reason: str | None
    quoted_total: Decimal
    approved_at: datetime | None
    closed_at: datetime | None
    created_at: datetime
    updated_at: datetime
    budget_items: list[BudgetItemResponse] = []

