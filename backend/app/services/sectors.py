from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.sector import Sector
from backend.app.schemas.sector import SectorCreate, SectorUpdate
from backend.app.services.crud import apply_updates

DEFAULT_ADMIN_SECTOR_NAME = "Administrativo"
DEFAULT_ADMIN_SECTOR_DESCRIPTION = "Setor administrativo padrao do sistema."


def list_sectors(db: Session, company_id: uuid.UUID) -> list[Sector]:
    statement = select(Sector).where(Sector.company_id == company_id).order_by(Sector.name)
    return list(db.scalars(statement))


def get_sector(db: Session, company_id: uuid.UUID, sector_id: uuid.UUID) -> Sector | None:
    statement = select(Sector).where(
        Sector.id == sector_id,
        Sector.company_id == company_id,
    )
    return db.scalars(statement).first()


def get_sector_by_name(db: Session, company_id: uuid.UUID, name: str) -> Sector | None:
    normalized_name = _normalize_name(name)
    for sector in list_sectors(db, company_id):
        if _normalize_name(sector.name) == normalized_name:
            return sector
    return None


def create_sector(db: Session, company_id: uuid.UUID, payload: SectorCreate) -> Sector:
    if get_sector_by_name(db, company_id, payload.name):
        raise ValueError("Sector name already exists for this company.")

    sector = Sector(
        company_id=company_id,
        name=payload.name,
        description=payload.description,
    )
    db.add(sector)
    db.commit()
    db.refresh(sector)
    return sector


def get_or_create_admin_sector(db: Session, company_id: uuid.UUID) -> Sector:
    sector = get_sector_by_name(db, company_id, DEFAULT_ADMIN_SECTOR_NAME)
    if sector is not None:
        return sector

    sector = Sector(
        company_id=company_id,
        name=DEFAULT_ADMIN_SECTOR_NAME,
        description=DEFAULT_ADMIN_SECTOR_DESCRIPTION,
    )
    db.add(sector)
    db.flush()
    return sector


def update_sector(
    db: Session,
    company_id: uuid.UUID,
    sector: Sector,
    payload: SectorUpdate,
) -> Sector:
    update_data = payload.model_dump(exclude_unset=True)
    new_name = update_data.get("name")
    if new_name:
        existing_sector = get_sector_by_name(db, company_id, new_name)
        if existing_sector and existing_sector.id != sector.id:
            raise ValueError("Sector name already exists for this company.")

    apply_updates(sector, payload)
    db.add(sector)
    db.commit()
    db.refresh(sector)
    return sector


def delete_sector(db: Session, company_id: uuid.UUID, sector: Sector) -> None:
    if (
        _normalize_name(sector.name) == _normalize_name(DEFAULT_ADMIN_SECTOR_NAME)
        and sector.company_id == company_id
    ):
        raise ValueError("Default administrative sector cannot be removed.")

    db.delete(sector)
    db.commit()


def _normalize_name(name: str) -> str:
    return name.strip().casefold()
