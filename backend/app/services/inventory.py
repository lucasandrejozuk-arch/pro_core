from __future__ import annotations

import uuid

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.models.inventory import InventoryItem
from backend.app.models.service_order import ServiceOrderBudgetItem
from backend.app.schemas.inventory import InventoryItemCreate, InventoryItemUpdate
from backend.app.services.crud import apply_updates


def list_inventory_items(db: Session, company_id: uuid.UUID) -> list[InventoryItem]:
    statement = (
        select(InventoryItem)
        .where(InventoryItem.company_id == company_id)
        .order_by(InventoryItem.created_at.desc())
    )
    return list(db.scalars(statement))


def get_inventory_item(
    db: Session,
    company_id: uuid.UUID,
    item_id: uuid.UUID,
) -> InventoryItem | None:
    statement = select(InventoryItem).where(
        InventoryItem.id == item_id,
        InventoryItem.company_id == company_id,
    )
    return db.scalars(statement).first()


def create_inventory_item(
    db: Session,
    company_id: uuid.UUID,
    payload: InventoryItemCreate,
) -> InventoryItem:
    item = InventoryItem(company_id=company_id, **payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def update_inventory_item(
    db: Session,
    item: InventoryItem,
    payload: InventoryItemUpdate,
) -> InventoryItem:
    apply_updates(item, payload)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def delete_inventory_item(db: Session, item: InventoryItem) -> None:
    db.execute(
        update(ServiceOrderBudgetItem)
        .where(ServiceOrderBudgetItem.inventory_item_id == item.id)
        .values(inventory_item_id=None)
    )
    db.delete(item)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ValueError("Item possui vinculos que impedem a exclusao.") from exc
