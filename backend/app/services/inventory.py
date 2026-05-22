from __future__ import annotations

import secrets
import uuid
from datetime import UTC, datetime

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.models.inventory import InventoryItem
from backend.app.models.service_order import ServiceOrderBudgetItem
from backend.app.schemas.inventory import InventoryItemCreate, InventoryItemUpdate
from backend.app.services.crud import apply_updates
from backend.app.services.inventory_rules import validate_inventory_category_requirements


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
    payload_data = payload.model_dump()
    sku = str(payload_data.get("sku") or "").strip().upper()
    generated_sku = not bool(sku)
    if generated_sku:
        sku = _generate_inventory_sku()
    payload_data["sku"] = sku
    technical_data = payload_data.pop("technical_data", None)
    validate_inventory_category_requirements(payload_data.get("category"), technical_data)

    attempts = 4 if generated_sku else 1
    for _ in range(attempts):
        item = InventoryItem(company_id=company_id, **payload_data)
        item.technical_data = technical_data
        db.add(item)
        try:
            db.commit()
            db.refresh(item)
            return item
        except IntegrityError as exc:
            db.rollback()
            if generated_sku:
                payload_data["sku"] = _generate_inventory_sku()
                continue
            raise ValueError("SKU ja cadastrado para esta empresa.") from exc

    raise ValueError("Nao foi possivel gerar SKU unico para o item.")


def _generate_inventory_sku() -> str:
    stamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
    suffix = secrets.token_hex(2).upper()
    return f"INV-{stamp}-{suffix}"


def update_inventory_item(
    db: Session,
    item: InventoryItem,
    payload: InventoryItemUpdate,
) -> InventoryItem:
    technical_data = (
        payload.technical_data if "technical_data" in payload.model_fields_set else None
    )
    target_category = payload.category if "category" in payload.model_fields_set else item.category
    target_technical_data = item.technical_data
    if "technical_data" in payload.model_fields_set:
        target_technical_data = technical_data
    validate_inventory_category_requirements(target_category, target_technical_data)
    apply_updates(item, payload)
    if "technical_data" in payload.model_fields_set:
        item.technical_data = technical_data
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
