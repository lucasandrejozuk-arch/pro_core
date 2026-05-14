from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.equipment import Equipment
from backend.app.schemas.equipment import EquipmentCreate, EquipmentUpdate
from backend.app.services.crud import apply_updates
from backend.app.services.customers import get_customer


def list_equipment(db: Session, company_id: uuid.UUID) -> list[Equipment]:
    statement = (
        select(Equipment)
        .where(Equipment.company_id == company_id)
        .order_by(Equipment.created_at.desc())
    )
    return list(db.scalars(statement))


def get_equipment(db: Session, company_id: uuid.UUID, equipment_id: uuid.UUID) -> Equipment | None:
    statement = select(Equipment).where(
        Equipment.id == equipment_id,
        Equipment.company_id == company_id,
    )
    return db.scalars(statement).first()


def create_equipment(db: Session, company_id: uuid.UUID, payload: EquipmentCreate) -> Equipment:
    if get_customer(db, company_id, payload.customer_id) is None:
        raise ValueError("Customer not found.")

    equipment = Equipment(company_id=company_id, **payload.model_dump())
    db.add(equipment)
    db.commit()
    db.refresh(equipment)
    return equipment


def update_equipment(db: Session, company_id: uuid.UUID, equipment: Equipment, payload: EquipmentUpdate) -> Equipment:
    if payload.customer_id is not None and get_customer(db, company_id, payload.customer_id) is None:
        raise ValueError("Customer not found.")

    apply_updates(equipment, payload)
    db.add(equipment)
    db.commit()
    db.refresh(equipment)
    return equipment

