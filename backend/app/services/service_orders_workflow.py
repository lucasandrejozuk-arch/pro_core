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
from sqlalchemy.orm import Session

from backend.app.models.enums import ServiceOrderEventSource, ServiceOrderStatus
from backend.app.models.service_order import (
    ServiceOrder,
    ServiceOrderEvent,
)
from backend.app.schemas.service_order import DiagnosisRequest, RejectServiceOrderRequest


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
    document.build(
        [
            Paragraph(f"Orcamento {service_order.code}", styles["Title"]),
            Paragraph(f"Cliente: {customer_name}", styles["Normal"]),
            Paragraph(f"Equipamento: {equipment_label or '-'}", styles["Normal"]),
            Paragraph(
                f"Diagnostico: {service_order.technical_diagnosis or '-'}",
                styles["Normal"],
            ),
            Spacer(1, 12),
            table,
            Spacer(1, 12),
            Paragraph(f"Total: R$ {service_order.quoted_total}", styles["Heading2"]),
        ]
    )
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


def recalculate_quoted_total(service_order: ServiceOrder) -> None:
    service_order.quoted_total = sum(
        (item.quantity or Decimal("0")) * (item.unit_price or Decimal("0"))
        for item in service_order.budget_items
    )
