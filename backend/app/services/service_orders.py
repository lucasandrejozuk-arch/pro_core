from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, selectinload

from backend.app.models.customer import Customer
from backend.app.models.enums import ServiceOrderEventSource, ServiceOrderStatus, UserRole
from backend.app.models.inventory import InventoryItem
from backend.app.models.service_order import (
    ServiceOrder,
    ServiceOrderBudgetItem,
)
from backend.app.models.user import User
from backend.app.schemas.service_order import (
    BudgetItemCreate,
    ServiceOrderCreate,
    ServiceOrderUpdate,
)
from backend.app.services.audit import create_audit_log
from backend.app.services.crud import apply_updates
from backend.app.services.customers import get_customer
from backend.app.services.equipment import get_equipment
from backend.app.services.service_orders_workflow import (
    add_service_order_event,
    recalculate_quoted_total,
)


def list_service_orders(
    db: Session,
    company_id: uuid.UUID,
    status: ServiceOrderStatus | None = None,
    assigned_technician_id: uuid.UUID | None = None,
    assigned_technician_ids: set[uuid.UUID] | None = None,
) -> list[ServiceOrder]:
    statement = (
        select(ServiceOrder)
        .options(
            selectinload(ServiceOrder.budget_items),
            selectinload(ServiceOrder.events),
            selectinload(ServiceOrder.documents),
            selectinload(ServiceOrder.customer),
            selectinload(ServiceOrder.equipment),
        )
        .where(ServiceOrder.company_id == company_id)
        .order_by(ServiceOrder.created_at.desc())
    )

    if status is not None:
        statement = statement.where(ServiceOrder.status == status)

    if assigned_technician_id is not None:
        statement = statement.where(ServiceOrder.assigned_technician_id == assigned_technician_id)

    if assigned_technician_ids is not None:
        if not assigned_technician_ids:
            return []
        statement = statement.where(
            ServiceOrder.assigned_technician_id.in_(assigned_technician_ids)
        )

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
            selectinload(ServiceOrder.events),
            selectinload(ServiceOrder.documents),
            selectinload(ServiceOrder.customer),
            selectinload(ServiceOrder.equipment),
        )
        .where(
            ServiceOrder.id == service_order_id,
            ServiceOrder.company_id == company_id,
        )
    )
    return db.scalars(statement).first()


def get_service_order_for_customer_portal(
    db: Session,
    code: str,
    customer_email: str,
) -> ServiceOrder | None:
    statement = (
        select(ServiceOrder)
        .join(Customer, Customer.id == ServiceOrder.customer_id)
        .options(
            selectinload(ServiceOrder.budget_items),
            selectinload(ServiceOrder.events),
            selectinload(ServiceOrder.documents),
            selectinload(ServiceOrder.customer),
            selectinload(ServiceOrder.equipment),
        )
        .where(
            func.lower(ServiceOrder.code) == code.strip().lower(),
            func.lower(Customer.email) == customer_email.strip().lower(),
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
    if equipment is None:
        raise ValueError("Equipment not found.")

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
    db.flush()
    add_service_order_event(
        db,
        service_order,
        "created",
        "Ordem de servico criada.",
        source=ServiceOrderEventSource.SYSTEM,
    )
    create_audit_log(
        db,
        company_id=company_id,
        action="service_order.created",
        entity_type="service_order",
        entity_id=service_order.id,
        summary=f"Ordem de servico {service_order.code} criada.",
    )
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
    add_service_order_event(
        db,
        service_order,
        "updated",
        "Ordem de servico atualizada.",
        metadata=payload.model_dump(exclude_unset=True),
    )
    create_audit_log(
        db,
        company_id=company_id,
        action="service_order.updated",
        entity_type="service_order",
        entity_id=service_order.id,
        summary=f"Ordem de servico {service_order.code} atualizada.",
        metadata=payload.model_dump(exclude_unset=True),
    )
    db.commit()
    db.refresh(service_order)
    return service_order


def delete_service_order(
    db: Session,
    service_order: ServiceOrder,
    actor_user_id: uuid.UUID,
) -> None:
    code = service_order.code
    company_id = service_order.company_id
    try:
        for document in list(service_order.documents):
            db.delete(document)
        for budget_item in list(service_order.budget_items):
            db.delete(budget_item)
        for event in list(service_order.events):
            db.delete(event)
        create_audit_log(
            db,
            company_id=company_id,
            actor_user_id=actor_user_id,
            action="service_order.deleted",
            entity_type="service_order",
            entity_id=service_order.id,
            summary=f"Ordem de servico {code} excluida.",
        )
        db.delete(service_order)
        db.commit()
    except SQLAlchemyError as exc:
        db.rollback()
        raise ValueError(
            "Nao foi possivel excluir a ordem de servico por vinculos operacionais."
        ) from exc


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
    add_service_order_event(
        db,
        service_order,
        "budget_item_added",
        f"Item de orcamento adicionado: {budget_item.description}.",
        metadata={
            "item_type": payload.item_type.value,
            "quantity": str(payload.quantity),
            "unit_price": str(payload.unit_price),
        },
    )
    db.commit()
    db.refresh(budget_item)
    return budget_item


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
