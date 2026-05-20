from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.api.dependencies import require_roles
from backend.app.db.session import get_db
from backend.app.models.enums import UserRole
from backend.app.models.user import User
from backend.app.schemas.customer import CustomerCreate, CustomerResponse, CustomerUpdate
from backend.app.services.customers import (
    create_customer,
    delete_customer,
    get_customer,
    list_customers,
    update_customer,
)

router = APIRouter(prefix="/customers", tags=["customers"])
customer_manager_user = require_roles(UserRole.ADMIN, UserRole.MANAGER)
CustomerManagerUser = Annotated[User, Depends(customer_manager_user)]
DbSession = Annotated[Session, Depends(get_db)]


@router.get("", response_model=list[CustomerResponse])
def list_customer_records(
    current_user: CustomerManagerUser,
    db: DbSession,
) -> list[CustomerResponse]:
    return list_customers(db, current_user.company_id)


@router.post("", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_customer_record(
    payload: CustomerCreate,
    current_user: CustomerManagerUser,
    db: DbSession,
) -> CustomerResponse:
    return create_customer(db, current_user.company_id, payload)


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer_record(
    customer_id: uuid.UUID,
    current_user: CustomerManagerUser,
    db: DbSession,
) -> CustomerResponse:
    customer = get_customer(db, current_user.company_id, customer_id)
    if customer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found.")

    return customer


@router.patch("/{customer_id}", response_model=CustomerResponse)
def update_customer_record(
    customer_id: uuid.UUID,
    payload: CustomerUpdate,
    current_user: CustomerManagerUser,
    db: DbSession,
) -> CustomerResponse:
    customer = get_customer(db, current_user.company_id, customer_id)
    if customer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found.")

    return update_customer(db, customer, payload)


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer_record(
    customer_id: uuid.UUID,
    current_user: CustomerManagerUser,
    db: DbSession,
) -> None:
    customer = get_customer(db, current_user.company_id, customer_id)
    if customer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found.")

    try:
        delete_customer(db, current_user.company_id, customer)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
