from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from backend.app.api.dependencies import require_roles
from backend.app.db.session import get_db
from backend.app.models.enums import ServiceOrderStatus, UserRole
from backend.app.models.user import User
from backend.app.schemas.service_order import (
    BudgetItemCreate,
    BudgetItemResponse,
    DiagnosisRequest,
    RejectServiceOrderRequest,
    ServiceOrderCreate,
    ServiceOrderResponse,
    ServiceOrderUpdate,
)
from backend.app.services.service_orders import (
    add_budget_item,
    approve_service_order,
    build_quote_pdf,
    complete_service_order,
    create_service_order,
    delete_service_order,
    get_service_order,
    list_service_orders,
    register_diagnosis,
    reject_service_order,
    start_service_order,
    submit_quote,
    update_service_order,
)
from backend.app.services.users import list_users_by_role

router = APIRouter(prefix="/service-orders", tags=["service-orders"])
staff_user = require_roles(UserRole.ADMIN, UserRole.MANAGER, UserRole.TECHNICIAN)
management_user = require_roles(UserRole.ADMIN, UserRole.MANAGER)


def _scoped_technician_ids(db: Session, current_user: User) -> set[uuid.UUID] | None:
    if current_user.role == UserRole.ADMIN:
        return None

    if current_user.role == UserRole.TECHNICIAN:
        return {current_user.id}

    if current_user.sector_id is None:
        return set()

    technicians = list_users_by_role(
        db,
        current_user.company_id,
        UserRole.TECHNICIAN,
        sector_id=current_user.sector_id,
    )
    return {technician.id for technician in technicians}


def _ensure_service_order_access(
    db: Session,
    current_user: User,
    service_order,
) -> None:
    allowed_technician_ids = _scoped_technician_ids(db, current_user)
    if allowed_technician_ids is None:
        return

    if service_order.assigned_technician_id in allowed_technician_ids:
        return

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Service order is outside the current user's operational scope.",
    )


def _ensure_assignment_scope(
    db: Session,
    current_user: User,
    assigned_technician_id: uuid.UUID | None,
) -> None:
    if current_user.role == UserRole.ADMIN or assigned_technician_id is None:
        return

    allowed_technician_ids = _scoped_technician_ids(db, current_user)
    if assigned_technician_id not in (allowed_technician_ids or set()):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Assigned technician is outside the current user's operational scope.",
        )


@router.get("", response_model=list[ServiceOrderResponse])
def list_service_order_records(
    status_filter: ServiceOrderStatus | None = Query(default=None, alias="status"),
    assigned_technician_id: uuid.UUID | None = None,
    current_user: User = Depends(staff_user),
    db: Session = Depends(get_db),
) -> list[ServiceOrderResponse]:
    assigned_technician_ids = _scoped_technician_ids(db, current_user)
    if assigned_technician_ids is not None and assigned_technician_id is not None:
        if assigned_technician_id not in assigned_technician_ids:
            return []
        assigned_technician_ids = None

    return list_service_orders(
        db=db,
        company_id=current_user.company_id,
        status=status_filter,
        assigned_technician_id=assigned_technician_id,
        assigned_technician_ids=assigned_technician_ids,
    )


@router.post("", response_model=ServiceOrderResponse, status_code=status.HTTP_201_CREATED)
def create_service_order_record(
    payload: ServiceOrderCreate,
    current_user: User = Depends(staff_user),
    db: Session = Depends(get_db),
) -> ServiceOrderResponse:
    _ensure_assignment_scope(db, current_user, payload.assigned_technician_id)
    try:
        return create_service_order(db, current_user.company_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/{service_order_id}", response_model=ServiceOrderResponse)
def get_service_order_record(
    service_order_id: uuid.UUID,
    current_user: User = Depends(staff_user),
    db: Session = Depends(get_db),
) -> ServiceOrderResponse:
    service_order = get_service_order(db, current_user.company_id, service_order_id)
    if service_order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Service order not found."
        )

    _ensure_service_order_access(db, current_user, service_order)
    return service_order


@router.patch("/{service_order_id}", response_model=ServiceOrderResponse)
def update_service_order_record(
    service_order_id: uuid.UUID,
    payload: ServiceOrderUpdate,
    current_user: User = Depends(staff_user),
    db: Session = Depends(get_db),
) -> ServiceOrderResponse:
    service_order = get_service_order(db, current_user.company_id, service_order_id)
    if service_order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Service order not found."
        )

    _ensure_service_order_access(db, current_user, service_order)
    if "assigned_technician_id" in payload.model_dump(exclude_unset=True):
        _ensure_assignment_scope(db, current_user, payload.assigned_technician_id)

    try:
        return update_service_order(db, current_user.company_id, service_order, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.delete("/{service_order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_service_order_record(
    service_order_id: uuid.UUID,
    current_user: User = Depends(management_user),
    db: Session = Depends(get_db),
) -> None:
    service_order = get_service_order(db, current_user.company_id, service_order_id)
    if service_order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Service order not found."
        )

    _ensure_service_order_access(db, current_user, service_order)
    delete_service_order(db, service_order, current_user.id)


@router.post("/{service_order_id}/diagnosis", response_model=ServiceOrderResponse)
def register_service_order_diagnosis(
    service_order_id: uuid.UUID,
    payload: DiagnosisRequest,
    current_user: User = Depends(staff_user),
    db: Session = Depends(get_db),
) -> ServiceOrderResponse:
    service_order = get_service_order(db, current_user.company_id, service_order_id)
    if service_order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Service order not found."
        )

    _ensure_service_order_access(db, current_user, service_order)
    return register_diagnosis(db, service_order, payload)


@router.post(
    "/{service_order_id}/budget-items",
    response_model=BudgetItemResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_service_order_budget_item(
    service_order_id: uuid.UUID,
    payload: BudgetItemCreate,
    current_user: User = Depends(staff_user),
    db: Session = Depends(get_db),
) -> BudgetItemResponse:
    service_order = get_service_order(db, current_user.company_id, service_order_id)
    if service_order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Service order not found."
        )

    _ensure_service_order_access(db, current_user, service_order)
    try:
        return add_budget_item(db, current_user.company_id, service_order, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/{service_order_id}/submit-quote", response_model=ServiceOrderResponse)
def submit_service_order_quote(
    service_order_id: uuid.UUID,
    current_user: User = Depends(staff_user),
    db: Session = Depends(get_db),
) -> ServiceOrderResponse:
    service_order = get_service_order(db, current_user.company_id, service_order_id)
    if service_order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Service order not found."
        )

    _ensure_service_order_access(db, current_user, service_order)
    return submit_quote(db, service_order)


@router.get("/{service_order_id}/quote.pdf")
def download_service_order_quote(
    service_order_id: uuid.UUID,
    current_user: User = Depends(staff_user),
    db: Session = Depends(get_db),
) -> Response:
    service_order = get_service_order(db, current_user.company_id, service_order_id)
    if service_order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Service order not found."
        )

    _ensure_service_order_access(db, current_user, service_order)
    return Response(
        content=build_quote_pdf(service_order),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{service_order.code}.pdf"'},
    )


@router.post("/{service_order_id}/approve", response_model=ServiceOrderResponse)
def approve_service_order_record(
    service_order_id: uuid.UUID,
    current_user: User = Depends(staff_user),
    db: Session = Depends(get_db),
) -> ServiceOrderResponse:
    service_order = get_service_order(db, current_user.company_id, service_order_id)
    if service_order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Service order not found."
        )

    _ensure_service_order_access(db, current_user, service_order)
    return approve_service_order(db, service_order)


@router.post("/{service_order_id}/reject", response_model=ServiceOrderResponse)
def reject_service_order_record(
    service_order_id: uuid.UUID,
    payload: RejectServiceOrderRequest,
    current_user: User = Depends(staff_user),
    db: Session = Depends(get_db),
) -> ServiceOrderResponse:
    service_order = get_service_order(db, current_user.company_id, service_order_id)
    if service_order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Service order not found."
        )

    _ensure_service_order_access(db, current_user, service_order)
    return reject_service_order(db, service_order, payload)


@router.post("/{service_order_id}/start", response_model=ServiceOrderResponse)
def start_service_order_record(
    service_order_id: uuid.UUID,
    current_user: User = Depends(staff_user),
    db: Session = Depends(get_db),
) -> ServiceOrderResponse:
    service_order = get_service_order(db, current_user.company_id, service_order_id)
    if service_order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Service order not found."
        )

    _ensure_service_order_access(db, current_user, service_order)
    return start_service_order(db, service_order)


@router.post("/{service_order_id}/complete", response_model=ServiceOrderResponse)
def complete_service_order_record(
    service_order_id: uuid.UUID,
    current_user: User = Depends(staff_user),
    db: Session = Depends(get_db),
) -> ServiceOrderResponse:
    service_order = get_service_order(db, current_user.company_id, service_order_id)
    if service_order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Service order not found."
        )

    _ensure_service_order_access(db, current_user, service_order)
    return complete_service_order(db, service_order)
