from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.api.dependencies import require_roles
from backend.app.db.session import get_db
from backend.app.models.enums import UserRole
from backend.app.models.user import User
from backend.app.schemas.equipment import EquipmentCreate, EquipmentResponse, EquipmentUpdate
from backend.app.services.equipment import (
    create_equipment,
    get_equipment,
    list_equipment,
    update_equipment,
)

router = APIRouter(prefix="/equipment", tags=["equipment"])
staff_user = require_roles(UserRole.ADMIN, UserRole.MANAGER, UserRole.TECHNICIAN)


@router.get("", response_model=list[EquipmentResponse])
def list_equipment_records(
    current_user: User = Depends(staff_user),
    db: Session = Depends(get_db),
) -> list[EquipmentResponse]:
    return list_equipment(db, current_user.company_id)


@router.post("", response_model=EquipmentResponse, status_code=status.HTTP_201_CREATED)
def create_equipment_record(
    payload: EquipmentCreate,
    current_user: User = Depends(staff_user),
    db: Session = Depends(get_db),
) -> EquipmentResponse:
    try:
        return create_equipment(db, current_user.company_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/{equipment_id}", response_model=EquipmentResponse)
def get_equipment_record(
    equipment_id: uuid.UUID,
    current_user: User = Depends(staff_user),
    db: Session = Depends(get_db),
) -> EquipmentResponse:
    equipment = get_equipment(db, current_user.company_id, equipment_id)
    if equipment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipment not found.")

    return equipment


@router.patch("/{equipment_id}", response_model=EquipmentResponse)
def update_equipment_record(
    equipment_id: uuid.UUID,
    payload: EquipmentUpdate,
    current_user: User = Depends(staff_user),
    db: Session = Depends(get_db),
) -> EquipmentResponse:
    equipment = get_equipment(db, current_user.company_id, equipment_id)
    if equipment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipment not found.")

    try:
        return update_equipment(db, current_user.company_id, equipment, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

