from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.api.dependencies import require_roles
from backend.app.db.session import get_db
from backend.app.models.enums import UserRole
from backend.app.models.sector import Sector
from backend.app.models.user import User
from backend.app.schemas.sector import SectorCreate, SectorResponse, SectorUpdate
from backend.app.services.sectors import (
    create_sector,
    get_sector,
    list_sectors,
    update_sector,
)

router = APIRouter(prefix="/sectors", tags=["sectors"])
admin_or_manager_user = require_roles(UserRole.ADMIN, UserRole.MANAGER)
admin_user = require_roles(UserRole.ADMIN)


@router.get("", response_model=list[SectorResponse])
def list_sector_records(
    current_user: User = Depends(admin_or_manager_user),
    db: Session = Depends(get_db),
) -> list[Sector]:
    if current_user.role == UserRole.MANAGER:
        if current_user.sector_id is None:
            return []
        sector = get_sector(db, current_user.company_id, current_user.sector_id)
        return [sector] if sector else []

    return list_sectors(db, current_user.company_id)


@router.post("", response_model=SectorResponse, status_code=status.HTTP_201_CREATED)
def create_sector_record(
    payload: SectorCreate,
    current_user: User = Depends(admin_user),
    db: Session = Depends(get_db),
) -> Sector:
    try:
        return create_sector(db, current_user.company_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.patch("/{sector_id}", response_model=SectorResponse)
def update_sector_record(
    sector_id: uuid.UUID,
    payload: SectorUpdate,
    current_user: User = Depends(admin_user),
    db: Session = Depends(get_db),
) -> Sector:
    sector = get_sector(db, current_user.company_id, sector_id)
    if sector is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sector not found.")

    try:
        return update_sector(db, current_user.company_id, sector, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
