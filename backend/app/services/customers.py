from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.customer import Customer
from backend.app.schemas.customer import CustomerCreate, CustomerUpdate
from backend.app.services.crud import apply_updates


def list_customers(db: Session, company_id: uuid.UUID) -> list[Customer]:
    statement = (
        select(Customer)
        .where(Customer.company_id == company_id)
        .order_by(Customer.created_at.desc())
    )
    return list(db.scalars(statement))


def get_customer(db: Session, company_id: uuid.UUID, customer_id: uuid.UUID) -> Customer | None:
    statement = select(Customer).where(
        Customer.id == customer_id,
        Customer.company_id == company_id,
    )
    return db.scalars(statement).first()


def create_customer(db: Session, company_id: uuid.UUID, payload: CustomerCreate) -> Customer:
    customer = Customer(company_id=company_id, **payload.model_dump())
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


def update_customer(db: Session, customer: Customer, payload: CustomerUpdate) -> Customer:
    apply_updates(customer, payload)
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer

