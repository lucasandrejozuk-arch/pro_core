from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.api.dependencies import require_roles
from backend.app.db.session import get_db
from backend.app.models.enums import UserRole
from backend.app.models.user import User
from backend.app.schemas.equipment import (
    EquipmentBoardComponentCreate,
    EquipmentBoardComponentResponse,
    EquipmentBoardComponentUpdate,
    EquipmentBoardCreate,
    EquipmentBoardResponse,
    EquipmentBoardUpdate,
    EquipmentCreate,
    EquipmentResponse,
    EquipmentUpdate,
)
from backend.app.services.equipment import (
    create_board_component,
    create_equipment,
    create_equipment_board,
    delete_board_component,
    delete_equipment,
    delete_equipment_board,
    get_board_component,
    get_equipment_board,
    get_equipment,
    list_equipment,
    update_board_component,
    update_equipment,
    update_equipment_board,
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


@router.delete("/{equipment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_equipment_record(
    equipment_id: uuid.UUID,
    current_user: User = Depends(staff_user),
    db: Session = Depends(get_db),
) -> None:
    equipment = get_equipment(db, current_user.company_id, equipment_id)
    if equipment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipment not found.")

    try:
        delete_equipment(db, current_user.company_id, equipment)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.post(
    "/{equipment_id}/boards",
    response_model=EquipmentBoardResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_equipment_board_record(
    equipment_id: uuid.UUID,
    payload: EquipmentBoardCreate,
    current_user: User = Depends(staff_user),
    db: Session = Depends(get_db),
) -> EquipmentBoardResponse:
    equipment = get_equipment(db, current_user.company_id, equipment_id)
    if equipment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipment not found.")

    return create_equipment_board(db, current_user.company_id, equipment, payload)


@router.patch("/{equipment_id}/boards/{board_id}", response_model=EquipmentBoardResponse)
def update_equipment_board_record(
    equipment_id: uuid.UUID,
    board_id: uuid.UUID,
    payload: EquipmentBoardUpdate,
    current_user: User = Depends(staff_user),
    db: Session = Depends(get_db),
) -> EquipmentBoardResponse:
    board = get_equipment_board(db, current_user.company_id, equipment_id, board_id)
    if board is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Board not found.")

    return update_equipment_board(db, board, payload)


@router.delete("/{equipment_id}/boards/{board_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_equipment_board_record(
    equipment_id: uuid.UUID,
    board_id: uuid.UUID,
    current_user: User = Depends(staff_user),
    db: Session = Depends(get_db),
) -> None:
    board = get_equipment_board(db, current_user.company_id, equipment_id, board_id)
    if board is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Board not found.")

    delete_equipment_board(db, board)


@router.post(
    "/{equipment_id}/boards/{board_id}/components",
    response_model=EquipmentBoardComponentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_board_component_record(
    equipment_id: uuid.UUID,
    board_id: uuid.UUID,
    payload: EquipmentBoardComponentCreate,
    current_user: User = Depends(staff_user),
    db: Session = Depends(get_db),
) -> EquipmentBoardComponentResponse:
    board = get_equipment_board(db, current_user.company_id, equipment_id, board_id)
    if board is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Board not found.")

    return create_board_component(db, current_user.company_id, board, payload)


@router.patch(
    "/{equipment_id}/boards/{board_id}/components/{component_id}",
    response_model=EquipmentBoardComponentResponse,
)
def update_board_component_record(
    equipment_id: uuid.UUID,
    board_id: uuid.UUID,
    component_id: uuid.UUID,
    payload: EquipmentBoardComponentUpdate,
    current_user: User = Depends(staff_user),
    db: Session = Depends(get_db),
) -> EquipmentBoardComponentResponse:
    board = get_equipment_board(db, current_user.company_id, equipment_id, board_id)
    if board is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Board not found.")

    component = get_board_component(db, current_user.company_id, board_id, component_id)
    if component is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Component not found.")

    return update_board_component(db, component, payload)


@router.delete(
    "/{equipment_id}/boards/{board_id}/components/{component_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_board_component_record(
    equipment_id: uuid.UUID,
    board_id: uuid.UUID,
    component_id: uuid.UUID,
    current_user: User = Depends(staff_user),
    db: Session = Depends(get_db),
) -> None:
    board = get_equipment_board(db, current_user.company_id, equipment_id, board_id)
    if board is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Board not found.")

    component = get_board_component(db, current_user.company_id, board_id, component_id)
    if component is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Component not found.")

    delete_board_component(db, component)
