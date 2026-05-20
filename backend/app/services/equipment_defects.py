from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.equipment import (
    Equipment,
    EquipmentDefectCase,
)
from backend.app.schemas.equipment import (
    EquipmentDefectCaseCreate,
    EquipmentDefectCaseUpdate,
)
from backend.app.services.crud import apply_updates
from backend.app.services.equipment_core import get_equipment_board


def list_defect_cases(
    db: Session,
    company_id: uuid.UUID,
    equipment_id: uuid.UUID,
    query: str = "",
) -> list[EquipmentDefectCase]:
    statement = (
        select(EquipmentDefectCase)
        .where(
            EquipmentDefectCase.company_id == company_id,
            EquipmentDefectCase.equipment_id == equipment_id,
        )
        .order_by(EquipmentDefectCase.updated_at.desc())
    )
    cases = list(db.scalars(statement))
    normalized_query = query.strip().lower()
    if not normalized_query:
        return cases

    return [
        defect_case
        for defect_case in cases
        if any(
            normalized_query in str(value or "").lower()
            for value in (
                defect_case.title,
                defect_case.symptom,
                defect_case.root_cause,
                defect_case.solution,
                defect_case.notes,
            )
        )
    ]


def get_defect_case(
    db: Session,
    company_id: uuid.UUID,
    equipment_id: uuid.UUID,
    case_id: uuid.UUID,
) -> EquipmentDefectCase | None:
    statement = select(EquipmentDefectCase).where(
        EquipmentDefectCase.id == case_id,
        EquipmentDefectCase.company_id == company_id,
        EquipmentDefectCase.equipment_id == equipment_id,
    )
    return db.scalars(statement).first()


def create_defect_case(
    db: Session,
    company_id: uuid.UUID,
    equipment: Equipment,
    payload: EquipmentDefectCaseCreate,
) -> EquipmentDefectCase:
    _validate_defect_case_board(db, company_id, equipment.id, payload.board_id)
    defect_case = EquipmentDefectCase(
        company_id=company_id,
        equipment_id=equipment.id,
        **payload.model_dump(),
    )
    db.add(defect_case)
    db.commit()
    db.refresh(defect_case)
    return defect_case


def update_defect_case(
    db: Session,
    company_id: uuid.UUID,
    equipment_id: uuid.UUID,
    defect_case: EquipmentDefectCase,
    payload: EquipmentDefectCaseUpdate,
) -> EquipmentDefectCase:
    if "board_id" in payload.model_dump(exclude_unset=True):
        _validate_defect_case_board(db, company_id, equipment_id, payload.board_id)
    apply_updates(defect_case, payload)
    db.add(defect_case)
    db.commit()
    db.refresh(defect_case)
    return defect_case


def delete_defect_case(db: Session, defect_case: EquipmentDefectCase) -> None:
    db.delete(defect_case)
    db.commit()


def _validate_defect_case_board(
    db: Session,
    company_id: uuid.UUID,
    equipment_id: uuid.UUID,
    board_id: uuid.UUID | None,
) -> None:
    if board_id is None:
        return
    if get_equipment_board(db, company_id, equipment_id, board_id) is None:
        raise ValueError("Board not found.")
