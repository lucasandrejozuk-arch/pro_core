from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from backend.app.models.enums import ServiceOrderStatus, UserRole
from backend.app.models.inventory import InventoryItem
from backend.app.models.service_order import ServiceOrder, ServiceOrderBudgetItem
from backend.app.models.user import User
from backend.app.schemas.service_order import (
    BudgetItemCreate,
    DiagnosisRequest,
    RejectServiceOrderRequest,
    ServiceOrderCreate,
    ServiceOrderUpdate,
)
from backend.app.services.crud import apply_updates
from backend.app.services.customers import get_customer
from backend.app.services.equipment import get_equipment


def list_service_orders(
    db: Session,
    company_id: uuid.UUID,
    status: ServiceOrderStatus | None = None,
    assigned_technician_id: uuid.UUID | None = None,
) -> list[ServiceOrder]:
    statement = (
        select(ServiceOrder)
        .options(
            selectinload(ServiceOrder.budget_items),
            selectinload(ServiceOrder.documents),
        )
        .where(ServiceOrder.company_id == company_id)
        .order_by(ServiceOrder.created_at.desc())
    )

    if status is not None:
        statement = statement.where(ServiceOrder.status == status)

    if assigned_technician_id is not None:
        statement = statement.where(ServiceOrder.assigned_technician_id == assigned_technician_id)

    return list(db.scalars(statement))


def get_service_order(
    db: Session,
    company_id: uuid.UUID,
    service_order_id: uuid.UUID,
) -> ServiceOrder | None:
    statement = (
        select(ServiceOrder)
        .options(
            selectinload(ServiceOrder.budget_items),
            selectinload(ServiceOrder.documents),
        )
        .where(
            ServiceOrder.id == service_order_id,
            ServiceOrder.company_id == company_id,
        )
    )
    return db.scalars(statement).first()


def create_service_order(
    db: Session,
    company_id: uuid.UUID,
    payload: ServiceOrderCreate,
) -> ServiceOrder:
    if get_customer(db, company_id, payload.customer_id) is None:
        raise ValueError("Customer not found.")

    equipment = get_equipment(db, company_id, payload.equipment_id)
    if equipment is None or equipment.customer_id != payload.customer_id:
        raise ValueError("Equipment not found for this customer.")

    if payload.assigned_technician_id is not None:
        validate_technician(db, company_id, payload.assigned_technician_id)

    service_order = ServiceOrder(
        company_id=company_id,
        code=generate_service_order_code(db, company_id),
        status=(
            ServiceOrderStatus.ASSIGNED
            if payload.assigned_technician_id
            else ServiceOrderStatus.OPEN
        ),
        **payload.model_dump(),
    )
    db.add(service_order)
    db.commit()
    db.refresh(service_order)
    return service_order


def update_service_order(
    db: Session,
    company_id: uuid.UUID,
    service_order: ServiceOrder,
    payload: ServiceOrderUpdate,
) -> ServiceOrder:
    if payload.assigned_technician_id is not None:
        validate_technician(db, company_id, payload.assigned_technician_id)

    apply_updates(service_order, payload)
    db.add(service_order)
    db.commit()
    db.refresh(service_order)
    return service_order


def register_diagnosis(
    db: Session,
    service_order: ServiceOrder,
    payload: DiagnosisRequest,
) -> ServiceOrder:
    service_order.technical_diagnosis = payload.technical_diagnosis
    service_order.status = ServiceOrderStatus.PENDING_QUOTE
    db.add(service_order)
    db.commit()
    db.refresh(service_order)
    return service_order


def add_budget_item(
    db: Session,
    company_id: uuid.UUID,
    service_order: ServiceOrder,
    payload: BudgetItemCreate,
) -> ServiceOrderBudgetItem:
    if payload.inventory_item_id is not None:
        inventory_item = db.get(InventoryItem, payload.inventory_item_id)
        if inventory_item is None or inventory_item.company_id != company_id:
            raise ValueError("Inventory item not found.")

    budget_item = ServiceOrderBudgetItem(
        service_order_id=service_order.id,
        **payload.model_dump(),
    )
    service_order.budget_items.append(budget_item)
    db.add(budget_item)
    db.flush()
    recalculate_quoted_total(service_order)
    db.add(service_order)
    db.commit()
    db.refresh(budget_item)
    return budget_item


def submit_quote(db: Session, service_order: ServiceOrder) -> ServiceOrder:
    service_order.status = ServiceOrderStatus.PENDING_APPROVAL
    db.add(service_order)
    db.commit()
    db.refresh(service_order)
    return service_order


def approve_service_order(db: Session, service_order: ServiceOrder) -> ServiceOrder:
    service_order.status = ServiceOrderStatus.APPROVED
    service_order.approved_at = datetime.now(UTC)
    db.add(service_order)
    db.commit()
    db.refresh(service_order)
    return service_order


def reject_service_order(
    db: Session,
    service_order: ServiceOrder,
    payload: RejectServiceOrderRequest,
) -> ServiceOrder:
    service_order.status = ServiceOrderStatus.REJECTED
    service_order.rejection_reason = payload.rejection_reason
    service_order.closed_at = datetime.now(UTC)
    db.add(service_order)
    db.commit()
    db.refresh(service_order)
    return service_order


def start_service_order(db: Session, service_order: ServiceOrder) -> ServiceOrder:
    service_order.status = ServiceOrderStatus.IN_PROGRESS
    db.add(service_order)
    db.commit()
    db.refresh(service_order)
    return service_order


def complete_service_order(db: Session, service_order: ServiceOrder) -> ServiceOrder:
    service_order.status = ServiceOrderStatus.COMPLETED
    service_order.closed_at = datetime.now(UTC)
    db.add(service_order)
    db.commit()
    db.refresh(service_order)
    return service_order


def generate_service_order_code(db: Session, company_id: uuid.UUID) -> str:
    total = db.scalar(
        select(func.count()).select_from(ServiceOrder).where(ServiceOrder.company_id == company_id)
    )
    return f"OS-{(total or 0) + 1:06d}"


def validate_technician(db: Session, company_id: uuid.UUID, user_id: uuid.UUID) -> None:
    user = db.get(User, user_id)
    if user is None or user.company_id != company_id:
        raise ValueError("Technician not found.")

    if user.role != UserRole.TECHNICIAN:
        raise ValueError("Assigned user must be a technician.")


def recalculate_quoted_total(service_order: ServiceOrder) -> None:
    service_order.quoted_total = sum(
        (item.quantity or Decimal("0")) * (item.unit_price or Decimal("0"))
        for item in service_order.budget_items
    )
