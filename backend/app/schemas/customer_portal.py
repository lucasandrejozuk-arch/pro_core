from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from backend.app.models.enums import BudgetItemType, ServiceOrderPriority, ServiceOrderStatus


class CustomerPortalLoginRequest(BaseModel):
    service_order_code: str = Field(min_length=1, max_length=40)
    email: str = Field(min_length=3, max_length=255)


class CustomerPortalLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    service_order: CustomerPortalServiceOrderResponse


class CustomerPortalBudgetItem(BaseModel):
    item_type: BudgetItemType
    description: str
    quantity: Decimal
    unit_price: Decimal


class CustomerPortalEvent(BaseModel):
    source: str
    event_type: str
    message: str
    created_at: datetime


class CustomerPortalServiceOrderResponse(BaseModel):
    id: UUID
    code: str
    customer_name: str
    equipment: str
    status: ServiceOrderStatus
    priority: ServiceOrderPriority
    problem_description: str
    technical_diagnosis: str | None
    quoted_total: Decimal
    sla_due_at: datetime | None
    quote_sent_at: datetime | None
    approved_at: datetime | None
    closed_at: datetime | None
    budget_items: list[CustomerPortalBudgetItem]
    events: list[CustomerPortalEvent]


class CustomerPortalRejectRequest(BaseModel):
    rejection_reason: str = Field(min_length=1, max_length=1000)
    decision_name: str | None = Field(default=None, max_length=160)


class CustomerPortalApproveRequest(BaseModel):
    decision_name: str | None = Field(default=None, max_length=160)
