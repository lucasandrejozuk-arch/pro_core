from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.api.dependencies import require_roles
from backend.app.db.session import get_db
from backend.app.models.enums import UserRole
from backend.app.models.user import User
from backend.app.schemas.customer import CustomerCreate, CustomerResponse, CustomerUpdate
from backend.app.services.customers import (
    create_customer,
    get_customer,
    list_customers,
    update_customer,
)

router = APIRouter(prefix="/customers", tags=["customers"])
staff_user = require_roles(UserRole.ADMIN, UserRole.MANAGER, UserRole.TECHNICIAN)


@router.get("", response_model=list[CustomerResponse])
def list_customer_records(
    current_user: User = Depends(staff_user),
    db: Session = Depends(get_db),
) -> list[CustomerResponse]:
    return list_customers(db, current_user.company_id)


@router.post("", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_customer_record(
    payload: CustomerCreate,
    current_user: User = Depends(staff_user),
    db: Session = Depends(get_db),
) -> CustomerResponse:
    return create_customer(db, current_user.company_id, payload)


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer_record(
    customer_id: uuid.UUID,
    current_user: User = Depends(staff_user),
    db: Session = Depends(get_db),
) -> CustomerResponse:
    customer = get_customer(db, current_user.company_id, customer_id)
    if customer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found.")

    return customer


@router.patch("/{customer_id}", response_model=CustomerResponse)
def update_customer_record(
    customer_id: uuid.UUID,
    payload: CustomerUpdate,
    current_user: User = Depends(staff_user),
    db: Session = Depends(get_db),
) -> CustomerResponse:
    customer = get_customer(db, current_user.company_id, customer_id)
    if customer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found.")

    return update_customer(db, customer, payload)

