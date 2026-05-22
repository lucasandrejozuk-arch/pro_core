from __future__ import annotations

import csv
from collections.abc import Iterable
from datetime import UTC, datetime
from decimal import Decimal
from io import BytesIO, StringIO
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from backend.app.models.equipment import (
    Equipment,
    EquipmentBoard,
    EquipmentBoardComponent,
    EquipmentDefectCase,
)


def build_equipment_export(
    equipment: Iterable[Equipment],
    export_format: str,
) -> tuple[bytes, str, str]:
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
    compact_rows = [row[:8] + [row[9], row[18], row[25]] for row in rows[:250]]
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
    document.build(
        [
            Paragraph("Relatorio de Equipamentos", styles["Title"]),
            Paragraph(
                "Equipamentos, objetos vinculados, componentes e casos de defeito.",
                styles["Normal"],
            ),
            Spacer(1, 12),
            table,
        ]
    )
    return output.getvalue()


def _serialize(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)
