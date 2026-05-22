from __future__ import annotations

import csv
import uuid
from decimal import Decimal, InvalidOperation
from io import StringIO
from typing import Any

from sqlalchemy.orm import Session

from backend.app.models.equipment import (
    Equipment,
    EquipmentBoard,
    EquipmentBoardComponent,
    EquipmentDefectCase,
)
from backend.app.services.equipment_catalog_exports import build_equipment_export
from backend.app.services.equipment_core import delete_equipment, list_equipment


def export_equipment_catalog(
    db: Session,
    company_id: uuid.UUID,
    export_format: str,
) -> tuple[bytes, str, str]:
    return build_equipment_export(list_equipment(db, company_id), export_format)


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
                        _row_value(row, "Componente Categoria", "Categoria Componente") or None
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
