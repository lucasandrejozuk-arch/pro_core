from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.api.dependencies import require_roles
from backend.app.db.session import get_db
from backend.app.models.enums import UserRole
from backend.app.models.user import User
from backend.app.schemas.inventory import (
    InventoryItemCreate,
    InventoryItemResponse,
    InventoryItemUpdate,
)
from backend.app.services.inventory import (
    create_inventory_item,
    get_inventory_item,
    list_inventory_items,
    update_inventory_item,
)

router = APIRouter(prefix="/inventory", tags=["inventory"])
inventory_user = require_roles(UserRole.ADMIN, UserRole.MANAGER)


@router.get("", response_model=list[InventoryItemResponse])
def list_inventory_records(
    current_user: User = Depends(inventory_user),
    db: Session = Depends(get_db),
) -> list[InventoryItemResponse]:
    return list_inventory_items(db, current_user.company_id)


@router.post("", response_model=InventoryItemResponse, status_code=status.HTTP_201_CREATED)
def create_inventory_record(
    payload: InventoryItemCreate,
    current_user: User = Depends(inventory_user),
    db: Session = Depends(get_db),
) -> InventoryItemResponse:
    return create_inventory_item(db, current_user.company_id, payload)


@router.get("/{item_id}", response_model=InventoryItemResponse)
def get_inventory_record(
    item_id: uuid.UUID,
    current_user: User = Depends(inventory_user),
    db: Session = Depends(get_db),
) -> InventoryItemResponse:
    item = get_inventory_item(db, current_user.company_id, item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory item not found.")

    return item


@router.patch("/{item_id}", response_model=InventoryItemResponse)
def update_inventory_record(
    item_id: uuid.UUID,
    payload: InventoryItemUpdate,
    current_user: User = Depends(inventory_user),
    db: Session = Depends(get_db),
) -> InventoryItemResponse:
    item = get_inventory_item(db, current_user.company_id, item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory item not found.")

    return update_inventory_item(db, item, payload)

