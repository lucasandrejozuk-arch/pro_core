from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from backend.app.core.config import get_settings
from backend.app.core.rate_limit import login_rate_limiter
from backend.app.core.security import create_access_token, decode_access_token
from backend.app.db.session import get_db
from backend.app.models.enums import ServiceOrderEventSource, ServiceOrderStatus
from backend.app.models.service_order import ServiceOrder
from backend.app.schemas.configuration import AppearanceSettingsResponse
from backend.app.schemas.customer_portal import (
    CustomerPortalApproveRequest,
    CustomerPortalLoginRequest,
    CustomerPortalLoginResponse,
    CustomerPortalRejectRequest,
    CustomerPortalServiceOrderResponse,
)
from backend.app.schemas.service_order import RejectServiceOrderRequest
from backend.app.services.configuration import get_appearance_settings
from backend.app.services.service_orders import (
    approve_service_order,
    build_quote_pdf,
    get_service_order,
    get_service_order_for_customer_portal,
    reject_service_order,
)

router = APIRouter(prefix="/customer-portal", tags=["customer-portal"])
bearer = HTTPBearer(auto_error=False)


def _get_portal_service_order(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> ServiceOrder:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing portal token."
        )

    try:
        payload = decode_access_token(credentials.credentials)
        if payload.get("scope") != "customer_portal":
            raise ValueError("Invalid scope.")
        company_id = uuid.UUID(str(payload["company_id"]))
        service_order_id = uuid.UUID(str(payload["service_order_id"]))
    except (KeyError, TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid portal token."
        ) from exc

    service_order = get_service_order(db, company_id, service_order_id)
    if service_order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Service order not found."
        )
    return service_order


@router.post("/login", response_model=CustomerPortalLoginResponse)
def login_customer_portal(
    request: Request,
    payload: CustomerPortalLoginRequest,
    db: Session = Depends(get_db),
) -> CustomerPortalLoginResponse:
    settings = get_settings()
    client_host = request.client.host if request.client else "unknown"
    rate_limit_key = (
        f"customer-portal:{client_host}:"
        f"{payload.service_order_code.strip().lower()}:{payload.email.strip().lower()}"
    )
    if login_rate_limiter.is_limited(
        key=rate_limit_key,
        max_attempts=settings.pro_core_public_rate_limit_attempts,
        window_seconds=settings.pro_core_public_rate_limit_window_seconds,
    ):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many portal login attempts. Try again later.",
        )

    service_order = get_service_order_for_customer_portal(
        db,
        code=payload.service_order_code,
        customer_email=payload.email,
    )
    if service_order is None:
        login_rate_limiter.record_failure(
            key=rate_limit_key,
            window_seconds=settings.pro_core_public_rate_limit_window_seconds,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid portal access."
        )

    login_rate_limiter.clear(rate_limit_key)
    token = create_access_token(
        str(service_order.id),
        extra_claims={
            "scope": "customer_portal",
            "company_id": str(service_order.company_id),
            "service_order_id": str(service_order.id),
        },
    )
    return CustomerPortalLoginResponse(
        access_token=token,
        service_order=_serialize_service_order(service_order),
    )


@router.get("/service-order", response_model=CustomerPortalServiceOrderResponse)
def get_customer_portal_service_order(
    service_order: ServiceOrder = Depends(_get_portal_service_order),
) -> CustomerPortalServiceOrderResponse:
    return _serialize_service_order(service_order)


@router.get("/appearance", response_model=AppearanceSettingsResponse)
def get_customer_portal_appearance(
    service_order: ServiceOrder = Depends(_get_portal_service_order),
    db: Session = Depends(get_db),
) -> AppearanceSettingsResponse:
    return get_appearance_settings(db, service_order.company_id)


@router.get("/quote.pdf")
def download_customer_portal_quote(
    service_order: ServiceOrder = Depends(_get_portal_service_order),
) -> Response:
    return Response(
        content=build_quote_pdf(service_order),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{service_order.code}.pdf"'},
    )


@router.post("/approve", response_model=CustomerPortalServiceOrderResponse)
def approve_customer_portal_quote(
    payload: CustomerPortalApproveRequest,
    service_order: ServiceOrder = Depends(_get_portal_service_order),
    db: Session = Depends(get_db),
) -> CustomerPortalServiceOrderResponse:
    _ensure_customer_decision_allowed(service_order)
    updated = approve_service_order(
        db,
        service_order,
        source=ServiceOrderEventSource.CUSTOMER,
        customer_decision_name=payload.decision_name,
    )
    return _serialize_service_order(updated)


@router.post("/reject", response_model=CustomerPortalServiceOrderResponse)
def reject_customer_portal_quote(
    payload: CustomerPortalRejectRequest,
    service_order: ServiceOrder = Depends(_get_portal_service_order),
    db: Session = Depends(get_db),
) -> CustomerPortalServiceOrderResponse:
    _ensure_customer_decision_allowed(service_order)
    updated = reject_service_order(
        db,
        service_order,
        RejectServiceOrderRequest(rejection_reason=payload.rejection_reason),
        source=ServiceOrderEventSource.CUSTOMER,
        customer_decision_name=payload.decision_name,
    )
    return _serialize_service_order(updated)


def _ensure_customer_decision_allowed(service_order: ServiceOrder) -> None:
    if service_order.status != ServiceOrderStatus.PENDING_APPROVAL:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quote is not awaiting customer approval.",
        )


def _serialize_service_order(service_order: ServiceOrder) -> CustomerPortalServiceOrderResponse:
    equipment = service_order.equipment
    equipment_label = " - ".join(
        part
        for part in [
            equipment.category if equipment else "",
            equipment.brand if equipment else "",
            equipment.model if equipment else "",
            equipment.serial_number if equipment else "",
        ]
        if part
    )
    return CustomerPortalServiceOrderResponse(
        id=service_order.id,
        code=service_order.code,
        customer_name=service_order.customer.name if service_order.customer else "-",
        equipment=equipment_label or "-",
        status=service_order.status,
        priority=service_order.priority,
        problem_description=service_order.problem_description,
        technical_diagnosis=service_order.technical_diagnosis,
        quoted_total=service_order.quoted_total,
        sla_due_at=service_order.sla_due_at,
        quote_sent_at=service_order.quote_sent_at,
        approved_at=service_order.approved_at,
        closed_at=service_order.closed_at,
        budget_items=[
            {
                "item_type": item.item_type,
                "description": item.description,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
            }
            for item in service_order.budget_items
        ],
        events=[
            {
                "source": event.source.value,
                "event_type": event.event_type,
                "message": event.message,
                "created_at": event.created_at,
            }
            for event in service_order.events
        ],
    )
