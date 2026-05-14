from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
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
    complete_service_order,
    create_service_order,
    get_service_order,
    list_service_orders,
    register_diagnosis,
    reject_service_order,
    start_service_order,
    submit_quote,
    update_service_order,
)

router = APIRouter(prefix="/service-orders", tags=["service-orders"])
staff_user = require_roles(UserRole.ADMIN, UserRole.MANAGER, UserRole.TECHNICIAN)


@router.get("", response_model=list[ServiceOrderResponse])
def list_service_order_records(
    status_filter: ServiceOrderStatus | None = Query(default=None, alias="status"),
    assigned_technician_id: uuid.UUID | None = None,
    current_user: User = Depends(staff_user),
    db: Session = Depends(get_db),
) -> list[ServiceOrderResponse]:
    return list_service_orders(
        db=db,
        company_id=current_user.company_id,
        status=status_filter,
        assigned_technician_id=assigned_technician_id,
    )


@router.post("", response_model=ServiceOrderResponse, status_code=status.HTTP_201_CREATED)
def create_service_order_record(
    payload: ServiceOrderCreate,
    current_user: User = Depends(staff_user),
    db: Session = Depends(get_db),
) -> ServiceOrderResponse:
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service order not found.")

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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service order not found.")

    try:
        return update_service_order(db, current_user.company_id, service_order, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/{service_order_id}/diagnosis", response_model=ServiceOrderResponse)
def register_service_order_diagnosis(
    service_order_id: uuid.UUID,
    payload: DiagnosisRequest,
    current_user: User = Depends(staff_user),
    db: Session = Depends(get_db),
) -> ServiceOrderResponse:
    service_order = get_service_order(db, current_user.company_id, service_order_id)
    if service_order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service order not found.")

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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service order not found.")

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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service order not found.")

    return submit_quote(db, service_order)


@router.post("/{service_order_id}/approve", response_model=ServiceOrderResponse)
def approve_service_order_record(
    service_order_id: uuid.UUID,
    current_user: User = Depends(staff_user),
    db: Session = Depends(get_db),
) -> ServiceOrderResponse:
    service_order = get_service_order(db, current_user.company_id, service_order_id)
    if service_order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service order not found.")

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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service order not found.")

    return reject_service_order(db, service_order, payload)


@router.post("/{service_order_id}/start", response_model=ServiceOrderResponse)
def start_service_order_record(
    service_order_id: uuid.UUID,
    current_user: User = Depends(staff_user),
    db: Session = Depends(get_db),
) -> ServiceOrderResponse:
    service_order = get_service_order(db, current_user.company_id, service_order_id)
    if service_order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service order not found.")

    return start_service_order(db, service_order)


@router.post("/{service_order_id}/complete", response_model=ServiceOrderResponse)
def complete_service_order_record(
    service_order_id: uuid.UUID,
    current_user: User = Depends(staff_user),
    db: Session = Depends(get_db),
) -> ServiceOrderResponse:
    service_order = get_service_order(db, current_user.company_id, service_order_id)
    if service_order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service order not found.")

    return complete_service_order(db, service_order)

