from __future__ import annotations

import uuid
from io import BytesIO
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import StreamingResponse
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
    EquipmentDefectCaseCreate,
    EquipmentDefectCaseResponse,
    EquipmentDefectCaseUpdate,
    EquipmentResponse,
    EquipmentUpdate,
)
from backend.app.services.equipment import (
    create_board_component,
    create_defect_case,
    create_equipment,
    create_equipment_board,
    delete_board_component,
    delete_defect_case,
    delete_equipment,
    delete_equipment_board,
    export_equipment_catalog,
    get_board_component,
    get_defect_case,
    get_equipment,
    get_equipment_board,
    import_equipment_catalog,
    list_defect_cases,
    list_equipment,
    update_board_component,
    update_defect_case,
    update_equipment,
    update_equipment_board,
)

router = APIRouter(prefix="/equipment", tags=["equipment"])
staff_user = require_roles(UserRole.ADMIN, UserRole.MANAGER, UserRole.TECHNICIAN)
StaffUser = Annotated[User, Depends(staff_user)]
DbSession = Annotated[Session, Depends(get_db)]
ExportFormat = Annotated[str, Query(alias="format", pattern="^(csv|pdf)$")]
CsvUploadFile = Annotated[UploadFile, File(alias="file")]


@router.get("", response_model=list[EquipmentResponse])
def list_equipment_records(
    current_user: StaffUser,
    db: DbSession,
) -> list[EquipmentResponse]:
    return list_equipment(db, current_user.company_id)


@router.get("/export")
def export_equipment_records(
    current_user: StaffUser,
    db: DbSession,
    export_format: ExportFormat = "csv",
) -> StreamingResponse:
    try:
        content, media_type, file_name = export_equipment_catalog(
            db,
            current_user.company_id,
            export_format,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return StreamingResponse(
        BytesIO(content),
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{file_name}"'},
    )


@router.post("/import")
async def import_equipment_records(
    upload_file: CsvUploadFile,
    current_user: StaffUser,
    db: DbSession,
    replace: bool = False,
) -> dict[str, int]:
    if not upload_file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="CSV file required.")
    try:
        content = await upload_file.read()
        return import_equipment_catalog(db, current_user.company_id, content, replace=replace)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.post("", response_model=EquipmentResponse, status_code=status.HTTP_201_CREATED)
def create_equipment_record(
    payload: EquipmentCreate,
    current_user: StaffUser,
    db: DbSession,
) -> EquipmentResponse:
    try:
        return create_equipment(db, current_user.company_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/{equipment_id}", response_model=EquipmentResponse)
def get_equipment_record(
    equipment_id: uuid.UUID,
    current_user: StaffUser,
    db: DbSession,
) -> EquipmentResponse:
    equipment = get_equipment(db, current_user.company_id, equipment_id)
    if equipment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipment not found.")

    return equipment


@router.patch("/{equipment_id}", response_model=EquipmentResponse)
def update_equipment_record(
    equipment_id: uuid.UUID,
    payload: EquipmentUpdate,
    current_user: StaffUser,
    db: DbSession,
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
    current_user: StaffUser,
    db: DbSession,
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
    current_user: StaffUser,
    db: DbSession,
) -> EquipmentBoardResponse:
    equipment = get_equipment(db, current_user.company_id, equipment_id)
    if equipment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipment not found.")

    return create_equipment_board(db, current_user.company_id, equipment, payload)


@router.get("/{equipment_id}/defect-cases", response_model=list[EquipmentDefectCaseResponse])
def list_equipment_defect_cases(
    equipment_id: uuid.UUID,
    current_user: StaffUser,
    db: DbSession,
    query: str = "",
) -> list[EquipmentDefectCaseResponse]:
    equipment = get_equipment(db, current_user.company_id, equipment_id)
    if equipment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipment not found.")

    return list_defect_cases(db, current_user.company_id, equipment_id, query=query)


@router.post(
    "/{equipment_id}/defect-cases",
    response_model=EquipmentDefectCaseResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_equipment_defect_case(
    equipment_id: uuid.UUID,
    payload: EquipmentDefectCaseCreate,
    current_user: StaffUser,
    db: DbSession,
) -> EquipmentDefectCaseResponse:
    equipment = get_equipment(db, current_user.company_id, equipment_id)
    if equipment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipment not found.")

    try:
        return create_defect_case(db, current_user.company_id, equipment, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.patch(
    "/{equipment_id}/defect-cases/{case_id}",
    response_model=EquipmentDefectCaseResponse,
)
def update_equipment_defect_case(
    equipment_id: uuid.UUID,
    case_id: uuid.UUID,
    payload: EquipmentDefectCaseUpdate,
    current_user: StaffUser,
    db: DbSession,
) -> EquipmentDefectCaseResponse:
    defect_case = get_defect_case(db, current_user.company_id, equipment_id, case_id)
    if defect_case is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Defect case not found.")

    try:
        return update_defect_case(db, current_user.company_id, equipment_id, defect_case, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.delete("/{equipment_id}/defect-cases/{case_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_equipment_defect_case(
    equipment_id: uuid.UUID,
    case_id: uuid.UUID,
    current_user: StaffUser,
    db: DbSession,
) -> None:
    defect_case = get_defect_case(db, current_user.company_id, equipment_id, case_id)
    if defect_case is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Defect case not found.")

    delete_defect_case(db, defect_case)


@router.patch("/{equipment_id}/boards/{board_id}", response_model=EquipmentBoardResponse)
def update_equipment_board_record(
    equipment_id: uuid.UUID,
    board_id: uuid.UUID,
    payload: EquipmentBoardUpdate,
    current_user: StaffUser,
    db: DbSession,
) -> EquipmentBoardResponse:
    board = get_equipment_board(db, current_user.company_id, equipment_id, board_id)
    if board is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Board not found.")

    return update_equipment_board(db, board, payload)


@router.delete("/{equipment_id}/boards/{board_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_equipment_board_record(
    equipment_id: uuid.UUID,
    board_id: uuid.UUID,
    current_user: StaffUser,
    db: DbSession,
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
    current_user: StaffUser,
    db: DbSession,
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
    current_user: StaffUser,
    db: DbSession,
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
    current_user: StaffUser,
    db: DbSession,
) -> None:
    board = get_equipment_board(db, current_user.company_id, equipment_id, board_id)
    if board is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Board not found.")

    component = get_board_component(db, current_user.company_id, board_id, component_id)
    if component is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Component not found.")

    delete_board_component(db, component)
