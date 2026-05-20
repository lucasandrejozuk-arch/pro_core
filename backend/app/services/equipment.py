from __future__ import annotations

import csv
import uuid
from collections.abc import Iterable
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from io import BytesIO, StringIO
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from backend.app.models.equipment import (
    Equipment,
    EquipmentBoard,
    EquipmentBoardComponent,
    EquipmentDefectCase,
)
from backend.app.models.service_order import ServiceOrder
from backend.app.schemas.equipment import (
    EquipmentBoardComponentCreate,
    EquipmentBoardComponentUpdate,
    EquipmentBoardCreate,
    EquipmentBoardUpdate,
    EquipmentCreate,
    EquipmentDefectCaseCreate,
    EquipmentDefectCaseUpdate,
    EquipmentUpdate,
)
from backend.app.services.crud import apply_updates
from backend.app.services.customers import get_customer


def list_equipment(db: Session, company_id: uuid.UUID) -> list[Equipment]:
    statement = (
        select(Equipment)
        .options(
            selectinload(Equipment.boards).selectinload(EquipmentBoard.components),
            selectinload(Equipment.defect_cases),
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
            selectinload(Equipment.defect_cases),
        )
        .where(
            Equipment.id == equipment_id,
            Equipment.company_id == company_id,
        )
    )
    return db.scalars(statement).first()


def create_equipment(db: Session, company_id: uuid.UUID, payload: EquipmentCreate) -> Equipment:
    if (
        payload.customer_id is not None
        and get_customer(db, company_id, payload.customer_id) is None
    ):
        raise ValueError("Customer not found.")

    equipment = Equipment(company_id=company_id, **payload.model_dump())
    db.add(equipment)
    db.commit()
    db.refresh(equipment)
    return equipment


def delete_equipment(db: Session, company_id: uuid.UUID, equipment: Equipment) -> None:
    linked_service_orders = db.scalar(
        select(func.count())
        .select_from(ServiceOrder)
        .where(
            ServiceOrder.company_id == company_id,
            ServiceOrder.equipment_id == equipment.id,
        )
    )
    if linked_service_orders:
        raise ValueError("Equipment is linked to service orders.")

    db.delete(equipment)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ValueError("Equipment is linked to service orders.") from exc


def update_equipment(
    db: Session,
    company_id: uuid.UUID,
    equipment: Equipment,
    payload: EquipmentUpdate,
) -> Equipment:
    if (
        payload.customer_id is not None
        and get_customer(db, company_id, payload.customer_id) is None
    ):
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


def delete_equipment_board(db: Session, board: EquipmentBoard) -> None:
    db.delete(board)
    db.commit()


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


def delete_board_component(db: Session, component: EquipmentBoardComponent) -> None:
    db.delete(component)
    db.commit()


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


def export_equipment_catalog(
    db: Session,
    company_id: uuid.UUID,
    export_format: str,
) -> tuple[bytes, str, str]:
    equipment = list_equipment(db, company_id)
    headers, rows = _equipment_export_rows(equipment)
    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    if export_format == "csv":
        return (
            _export_catalog_csv(headers, rows),
            "text/csv; charset=utf-8",
            f"equipment_{timestamp}.csv",
        )
    if export_format == "pdf":
        return (
            _export_catalog_pdf(headers, rows),
            "application/pdf",
            f"equipment_{timestamp}.pdf",
        )
    raise ValueError("Unsupported export format.")


def import_equipment_catalog(
    db: Session,
    company_id: uuid.UUID,
    content: bytes,
    replace: bool = False,
) -> dict[str, int]:
    text = content.decode("utf-8-sig")
    first_line = text.splitlines()[0] if text.splitlines() else ""
    delimiter = ";" if ";" in first_line else ","
    reader = csv.DictReader(StringIO(text), delimiter=delimiter)
    rows = list(reader)

    if replace:
        for equipment in list_equipment(db, company_id):
            delete_equipment(db, company_id, equipment)

    existing_equipment = list_equipment(db, company_id)
    equipment_index = {
        _equipment_import_key(equipment): equipment for equipment in existing_equipment
    }
    board_index: dict[tuple[Any, ...], EquipmentBoard] = {}
    for equipment in existing_equipment:
        for board in equipment.boards:
            board_index[_board_import_key(equipment.id, board)] = board

    processed_rows = 0
    created_equipment = 0
    created_boards = 0
    created_components = 0
    created_cases = 0

    for row in rows:
        category = _row_value(row, "Tipo", "Categoria")
        brand = _row_value(row, "Marca")
        model = _row_value(row, "Modelo")
        special_number = _row_value(row, "No Especial Equip", "N Especial Equip")
        serial_number = _row_value(row, "No Serie Equip", "Serie")
        if not any((category, brand, model, special_number, serial_number)):
            continue

        equipment_key = (category, brand, model, special_number, serial_number)
        equipment = equipment_index.get(equipment_key)
        if equipment is None:
            equipment = Equipment(
                company_id=company_id,
                category=category or "Equipamento",
                brand=brand or None,
                model=model or None,
                special_number=special_number or None,
                serial_number=serial_number or None,
                unit_price=_decimal_from_text(_row_value(row, "Valor Equip", "Valor Unitario")),
                description=_row_value(row, "Notas Equip", "Descricao") or None,
            )
            db.add(equipment)
            db.flush()
            equipment_index[equipment_key] = equipment
            created_equipment += 1

        board_name = _row_value(row, "Objeto Nome", "Placa", "Nome Objeto")
        board_special = _row_value(row, "No Especial Obj", "Nº Especial Obj")
        board_serial = _row_value(row, "No Serie Obj", "Nº Série Obj")
        board_model = _row_value(row, "Modelo Obj", "Modelo Objeto")
        board_revision = _row_value(row, "Revisao Obj", "Revisão Obj")
        board: EquipmentBoard | None = None
        if any((board_name, board_special, board_serial, board_model, board_revision)):
            board_key = (
                equipment.id,
                board_name,
                board_special,
                board_serial,
                board_model,
                board_revision,
            )
            board = board_index.get(board_key)
            if board is None:
                board = EquipmentBoard(
                    company_id=company_id,
                    equipment_id=equipment.id,
                    name=board_name or "Objeto vinculado",
                    special_number=board_special or None,
                    serial_number=board_serial or None,
                    model=board_model or None,
                    revision=board_revision or None,
                    unit_price=_decimal_from_text(_row_value(row, "Valor Obj")),
                    notes=_row_value(row, "Notas Obj") or None,
                )
                db.add(board)
                db.flush()
                board_index[board_key] = board
                created_boards += 1

        component_name = _row_value(row, "Componente Dados", "Componente", "Dados")
        if board is not None and any(
            (
                component_name,
                _row_value(row, "Componente Categoria", "Categoria Componente"),
                _row_value(row, "Part Number"),
                _row_value(row, "Localizacao", "Localização"),
                _row_value(row, "Obs Componente"),
            )
        ):
            db.add(
                EquipmentBoardComponent(
                    company_id=company_id,
                    board_id=board.id,
                    category=(
                        _row_value(row, "Componente Categoria", "Categoria Componente")
                        or None
                    ),
                    name=component_name or "Componente",
                    quantity=_row_value(row, "Quantidade") or None,
                    part_number=_row_value(row, "Part Number") or None,
                    location=_row_value(row, "Localizacao", "Localização") or None,
                    unit_price=_decimal_from_text(_row_value(row, "Valor Componente")),
                    notes=_row_value(row, "Obs Componente") or None,
                )
            )
            created_components += 1

        case_title = _row_value(row, "Caso Titulo", "Caso Título")
        if any(
            (
                case_title,
                _row_value(row, "Caso Sintoma"),
                _row_value(row, "Caso Causa"),
                _row_value(row, "Caso Solucao", "Caso Solução"),
                _row_value(row, "Obs Caso"),
            )
        ):
            db.add(
                EquipmentDefectCase(
                    company_id=company_id,
                    equipment_id=equipment.id,
                    board_id=board.id if board is not None else None,
                    title=case_title or "Caso de defeito",
                    symptom=_row_value(row, "Caso Sintoma") or None,
                    root_cause=_row_value(row, "Caso Causa") or None,
                    solution=_row_value(row, "Caso Solucao", "Caso Solução") or None,
                    notes=_row_value(row, "Obs Caso") or None,
                )
            )
            created_cases += 1

        processed_rows += 1

    db.commit()
    return {
        "processed_rows": processed_rows,
        "created_equipment": created_equipment,
        "created_boards": created_boards,
        "created_components": created_components,
        "created_defect_cases": created_cases,
    }


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


def _equipment_export_rows(
    equipment_items: Iterable[Equipment],
) -> tuple[list[str], list[list[str]]]:
    headers = [
        "Equipamento ID",
        "Tipo",
        "Marca",
        "Modelo",
        "No Especial Equip",
        "No Serie Equip",
        "Valor Equip",
        "Notas Equip",
        "Objeto ID",
        "Objeto Nome",
        "No Especial Obj",
        "No Serie Obj",
        "Modelo Obj",
        "Revisao Obj",
        "Valor Obj",
        "Notas Obj",
        "Componente ID",
        "Componente Categoria",
        "Componente Dados",
        "Quantidade",
        "Part Number",
        "Localizacao",
        "Valor Componente",
        "Obs Componente",
        "Caso ID",
        "Caso Titulo",
        "Caso Sintoma",
        "Caso Causa",
        "Caso Solucao",
        "Obs Caso",
    ]
    rows: list[list[str]] = []
    for equipment in equipment_items:
        boards = equipment.boards or []
        equipment_cases = [case for case in equipment.defect_cases if case.board_id is None]
        if not boards and not equipment_cases:
            rows.append(_equipment_row(equipment))
            continue
        if equipment_cases:
            for defect_case in equipment_cases:
                rows.append(_equipment_row(equipment, defect_case=defect_case))
        for board in boards:
            components = board.components or []
            defect_cases = [case for case in equipment.defect_cases if case.board_id == board.id]
            if not components and not defect_cases:
                rows.append(_equipment_row(equipment, board=board))
                continue
            max_len = max(len(components), len(defect_cases), 1)
            for index in range(max_len):
                rows.append(
                    _equipment_row(
                        equipment,
                        board=board,
                        component=components[index] if index < len(components) else None,
                        defect_case=defect_cases[index] if index < len(defect_cases) else None,
                    )
                )
    return headers, rows


def _equipment_row(
    equipment: Equipment,
    board: EquipmentBoard | None = None,
    component: EquipmentBoardComponent | None = None,
    defect_case: EquipmentDefectCase | None = None,
) -> list[str]:
    return [
        str(equipment.id),
        _serialize(equipment.category),
        _serialize(equipment.brand),
        _serialize(equipment.model),
        _serialize(equipment.special_number),
        _serialize(equipment.serial_number),
        _serialize(equipment.unit_price),
        _serialize(equipment.description),
        str(board.id) if board else "",
        _serialize(board.name if board else ""),
        _serialize(board.special_number if board else ""),
        _serialize(board.serial_number if board else ""),
        _serialize(board.model if board else ""),
        _serialize(board.revision if board else ""),
        _serialize(board.unit_price if board else ""),
        _serialize(board.notes if board else ""),
        str(component.id) if component else "",
        _serialize(component.category if component else ""),
        _serialize(component.name if component else ""),
        _serialize(component.quantity if component else ""),
        _serialize(component.part_number if component else ""),
        _serialize(component.location if component else ""),
        _serialize(component.unit_price if component else ""),
        _serialize(component.notes if component else ""),
        str(defect_case.id) if defect_case else "",
        _serialize(defect_case.title if defect_case else ""),
        _serialize(defect_case.symptom if defect_case else ""),
        _serialize(defect_case.root_cause if defect_case else ""),
        _serialize(defect_case.solution if defect_case else ""),
        _serialize(defect_case.notes if defect_case else ""),
    ]


def _export_catalog_csv(headers: list[str], rows: list[list[str]]) -> bytes:
    output = StringIO()
    writer = csv.writer(output, delimiter=";")
    writer.writerow(headers)
    writer.writerows(rows)
    return output.getvalue().encode("utf-8-sig")


def _export_catalog_pdf(headers: list[str], rows: list[list[str]]) -> bytes:
    output = BytesIO()
    document = SimpleDocTemplate(output, pagesize=landscape(A4))
    styles = getSampleStyleSheet()
    compact_headers = headers[:8] + ["Objeto Nome", "Componente Dados", "Caso Titulo"]
    compact_rows = [
        row[:8] + [row[9], row[18], row[25]]
        for row in rows[:250]
    ]
    table = Table([compact_headers, *compact_rows], repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#edf3fb")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#172033")),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#d8e0ea")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 7),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    elements = [
        Paragraph("Relatorio de Equipamentos", styles["Title"]),
        Paragraph(
            "Equipamentos, objetos vinculados, componentes e casos de defeito.",
            styles["Normal"],
        ),
        Spacer(1, 12),
        table,
    ]
    document.build(elements)
    return output.getvalue()


def _equipment_import_key(equipment: Equipment) -> tuple[str, str, str, str, str]:
    return (
        equipment.category or "",
        equipment.brand or "",
        equipment.model or "",
        equipment.special_number or "",
        equipment.serial_number or "",
    )


def _board_import_key(equipment_id: uuid.UUID, board: EquipmentBoard) -> tuple[Any, ...]:
    return (
        equipment_id,
        board.name or "",
        board.special_number or "",
        board.serial_number or "",
        board.model or "",
        board.revision or "",
    )


def _row_value(row: dict[str, Any], *keys: str) -> str:
    for key in keys:
        value = row.get(key)
        if value is not None:
            return str(value).strip()
    return ""


def _decimal_from_text(value: str) -> Decimal:
    normalized = value.strip()
    if not normalized:
        return Decimal("0")
    if "," in normalized:
        normalized = normalized.replace(".", "").replace(",", ".")
    try:
        decimal_value = Decimal(normalized)
    except InvalidOperation:
        return Decimal("0")
    return max(decimal_value, Decimal("0"))


def _serialize(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)
