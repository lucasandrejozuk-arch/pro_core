from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime
from decimal import Decimal
from io import BytesIO
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, selectinload

from backend.app.models.customer import Customer
from backend.app.models.enums import ServiceOrderEventSource, ServiceOrderStatus, UserRole
from backend.app.models.inventory import InventoryItem
from backend.app.models.service_order import (
    ServiceOrder,
    ServiceOrderBudgetItem,
    ServiceOrderEvent,
)
from backend.app.models.user import User
from backend.app.schemas.service_order import (
    BudgetItemCreate,
    DiagnosisRequest,
    RejectServiceOrderRequest,
    ServiceOrderCreate,
    ServiceOrderUpdate,
)
from backend.app.services.audit import create_audit_log
from backend.app.services.crud import apply_updates
from backend.app.services.customers import get_customer
from backend.app.services.equipment import get_equipment


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
    for document in list(service_order.documents):
        db.delete(document)
    create_audit_log(
        db,
        company_id=company_id,
        actor_user_id=actor_user_id,
        action="service_order.deleted",
        entity_type="service_order",
        entity_id=service_order.id,
        summary=f"Ordem de servico {code} excluida.",
    )
    try:
        db.delete(service_order)
        db.commit()
    except SQLAlchemyError as exc:
        db.rollback()
        raise ValueError(
            "Nao foi possivel excluir a ordem de servico por vinculos operacionais."
        ) from exc


def register_diagnosis(
    db: Session,
    service_order: ServiceOrder,
    payload: DiagnosisRequest,
) -> ServiceOrder:
    service_order.technical_diagnosis = payload.technical_diagnosis
    service_order.status = ServiceOrderStatus.PENDING_QUOTE
    db.add(service_order)
    add_service_order_event(
        db,
        service_order,
        "diagnosis_registered",
        "Diagnostico tecnico registrado.",
    )
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


def submit_quote(db: Session, service_order: ServiceOrder) -> ServiceOrder:
    service_order.status = ServiceOrderStatus.PENDING_APPROVAL
    service_order.quote_sent_at = datetime.now(UTC)
    db.add(service_order)
    add_service_order_event(
        db,
        service_order,
        "quote_sent",
        "Orcamento enviado para aprovacao do cliente.",
    )
    db.commit()
    db.refresh(service_order)
    return service_order


def approve_service_order(
    db: Session,
    service_order: ServiceOrder,
    source: ServiceOrderEventSource = ServiceOrderEventSource.STAFF,
    customer_decision_name: str | None = None,
) -> ServiceOrder:
    service_order.status = ServiceOrderStatus.APPROVED
    service_order.approved_at = datetime.now(UTC)
    service_order.customer_decision_at = service_order.approved_at
    service_order.customer_decision_name = customer_decision_name
    service_order.approval_source = source.value
    db.add(service_order)
    add_service_order_event(
        db,
        service_order,
        "quote_approved",
        "Orcamento aprovado.",
        source=source,
        metadata={"customer_decision_name": customer_decision_name},
    )
    db.commit()
    db.refresh(service_order)
    return service_order


def reject_service_order(
    db: Session,
    service_order: ServiceOrder,
    payload: RejectServiceOrderRequest,
    source: ServiceOrderEventSource = ServiceOrderEventSource.STAFF,
    customer_decision_name: str | None = None,
) -> ServiceOrder:
    service_order.status = ServiceOrderStatus.REJECTED
    service_order.rejection_reason = payload.rejection_reason
    service_order.customer_decision_at = datetime.now(UTC)
    service_order.customer_decision_name = customer_decision_name
    service_order.approval_source = source.value
    service_order.closed_at = datetime.now(UTC)
    db.add(service_order)
    add_service_order_event(
        db,
        service_order,
        "quote_rejected",
        "Orcamento reprovado.",
        source=source,
        metadata={
            "rejection_reason": payload.rejection_reason,
            "customer_decision_name": customer_decision_name,
        },
    )
    db.commit()
    db.refresh(service_order)
    return service_order


def start_service_order(db: Session, service_order: ServiceOrder) -> ServiceOrder:
    service_order.status = ServiceOrderStatus.IN_PROGRESS
    db.add(service_order)
    add_service_order_event(
        db,
        service_order,
        "execution_started",
        "Execucao do servico iniciada.",
    )
    db.commit()
    db.refresh(service_order)
    return service_order


def complete_service_order(db: Session, service_order: ServiceOrder) -> ServiceOrder:
    service_order.status = ServiceOrderStatus.COMPLETED
    service_order.closed_at = datetime.now(UTC)
    db.add(service_order)
    add_service_order_event(
        db,
        service_order,
        "completed",
        "Ordem de servico concluida.",
    )
    db.commit()
    db.refresh(service_order)
    return service_order


def build_quote_pdf(service_order: ServiceOrder) -> bytes:
    output = BytesIO()
    document = SimpleDocTemplate(output, pagesize=A4, rightMargin=36, leftMargin=36)
    styles = getSampleStyleSheet()
    customer_name = service_order.customer.name if service_order.customer else "-"
    equipment_label = " - ".join(
        part
        for part in [
            service_order.equipment.category if service_order.equipment else "",
            service_order.equipment.brand if service_order.equipment else "",
            service_order.equipment.model if service_order.equipment else "",
            service_order.equipment.serial_number if service_order.equipment else "",
        ]
        if part
    )
    rows = [["Tipo", "Descricao", "Qtd", "Valor unit.", "Total"]]
    for item in service_order.budget_items:
        total = (item.quantity or Decimal("0")) * (item.unit_price or Decimal("0"))
        rows.append(
            [
                item.item_type.value,
                item.description,
                str(item.quantity),
                f"R$ {item.unit_price}",
                f"R$ {total}",
            ]
        )

    table = Table(rows, repeatRows=1, colWidths=[70, 210, 50, 80, 80])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#edf3fb")),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#d8e0ea")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    elements = [
        Paragraph(f"Orcamento {service_order.code}", styles["Title"]),
        Paragraph(f"Cliente: {customer_name}", styles["Normal"]),
        Paragraph(f"Equipamento: {equipment_label or '-'}", styles["Normal"]),
        Paragraph(f"Diagnostico: {service_order.technical_diagnosis or '-'}", styles["Normal"]),
        Spacer(1, 12),
        table,
        Spacer(1, 12),
        Paragraph(f"Total: R$ {service_order.quoted_total}", styles["Heading2"]),
    ]
    document.build(elements)
    return output.getvalue()


def add_service_order_event(
    db: Session,
    service_order: ServiceOrder,
    event_type: str,
    message: str,
    source: ServiceOrderEventSource = ServiceOrderEventSource.STAFF,
    actor_user_id: uuid.UUID | None = None,
    metadata: dict[str, Any] | None = None,
) -> ServiceOrderEvent:
    event = ServiceOrderEvent(
        company_id=service_order.company_id,
        service_order_id=service_order.id,
        actor_user_id=actor_user_id,
        source=source,
        event_type=event_type,
        message=message,
        metadata_json=json.dumps(metadata, default=str) if metadata else None,
    )
    service_order.events.append(event)
    db.add(event)
    return event


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
