from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from backend.app.models.equipment import Equipment, EquipmentBoard, EquipmentBoardComponent
from backend.app.schemas.equipment import EquipmentCreate, EquipmentUpdate
from backend.app.schemas.equipment import (
    EquipmentBoardComponentCreate,
    EquipmentBoardComponentUpdate,
    EquipmentBoardCreate,
    EquipmentBoardUpdate,
)
from backend.app.services.crud import apply_updates
from backend.app.services.customers import get_customer


def list_equipment(db: Session, company_id: uuid.UUID) -> list[Equipment]:
    statement = (
        select(Equipment)
        .options(
            selectinload(Equipment.boards).selectinload(EquipmentBoard.components),
        )
        .where(Equipment.company_id == company_id)
        .order_by(Equipment.created_at.desc())
    )
    return list(db.scalars(statement))


def get_equipment(db: Session, company_id: uuid.UUID, equipment_id: uuid.UUID) -> Equipment | None:
    statement = (
        select(Equipment)
        .options(
            selectinload(Equipment.boards).selectinload(EquipmentBoard.components),
        )
        .where(
            Equipment.id == equipment_id,
            Equipment.company_id == company_id,
        )
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


def get_equipment_board(
    db: Session,
    company_id: uuid.UUID,
    equipment_id: uuid.UUID,
    board_id: uuid.UUID,
) -> EquipmentBoard | None:
    statement = (
        select(EquipmentBoard)
        .options(selectinload(EquipmentBoard.components))
        .where(
            EquipmentBoard.id == board_id,
            EquipmentBoard.company_id == company_id,
            EquipmentBoard.equipment_id == equipment_id,
        )
    )
    return db.scalars(statement).first()


def get_board_component(
    db: Session,
    company_id: uuid.UUID,
    board_id: uuid.UUID,
    component_id: uuid.UUID,
) -> EquipmentBoardComponent | None:
    statement = select(EquipmentBoardComponent).where(
        EquipmentBoardComponent.id == component_id,
        EquipmentBoardComponent.company_id == company_id,
        EquipmentBoardComponent.board_id == board_id,
    )
    return db.scalars(statement).first()


def create_equipment_board(
    db: Session,
    company_id: uuid.UUID,
    equipment: Equipment,
    payload: EquipmentBoardCreate,
) -> EquipmentBoard:
    board = EquipmentBoard(
        company_id=company_id,
        equipment_id=equipment.id,
        **payload.model_dump(),
    )
    db.add(board)
    db.commit()
    db.refresh(board)
    return board


def update_equipment_board(
    db: Session,
    board: EquipmentBoard,
    payload: EquipmentBoardUpdate,
) -> EquipmentBoard:
    apply_updates(board, payload)
    db.add(board)
    db.commit()
    db.refresh(board)
    return board


def create_board_component(
    db: Session,
    company_id: uuid.UUID,
    board: EquipmentBoard,
    payload: EquipmentBoardComponentCreate,
) -> EquipmentBoardComponent:
    component = EquipmentBoardComponent(
        company_id=company_id,
        board_id=board.id,
        **payload.model_dump(),
    )
    db.add(component)
    db.commit()
    db.refresh(component)
    return component


def update_board_component(
    db: Session,
    component: EquipmentBoardComponent,
    payload: EquipmentBoardComponentUpdate,
) -> EquipmentBoardComponent:
    apply_updates(component, payload)
    db.add(component)
    db.commit()
    db.refresh(component)
    return component
