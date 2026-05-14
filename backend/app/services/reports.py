from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from io import BytesIO, StringIO
from typing import Any, Callable

from openpyxl import Workbook
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Spacer, Table, TableStyle, Paragraph
from reportlab.lib import colors
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.customer import Customer
from backend.app.models.equipment import Equipment
from backend.app.models.inventory import InventoryItem
from backend.app.models.service_order import ServiceOrder
from backend.app.models.user import User


@dataclass(frozen=True)
class ReportColumnSpec:
    key: str
    label: str
    getter: Callable[[Any], Any]


@dataclass(frozen=True)
class ReportSpec:
    title: str
    model: type
    columns: tuple[ReportColumnSpec, ...]


REPORT_SPECS: dict[str, ReportSpec] = {
    "customers": ReportSpec(
        title="Relatorio de Clientes",
        model=Customer,
        columns=(
            ReportColumnSpec("name", "Nome", lambda item: item.name),
            ReportColumnSpec("email", "Email", lambda item: item.email),
            ReportColumnSpec("phone", "Telefone", lambda item: item.phone),
            ReportColumnSpec("is_active", "Ativo", lambda item: item.is_active),
            ReportColumnSpec("created_at", "Criado em", lambda item: item.created_at),
        ),
    ),
    "equipment": ReportSpec(
        title="Relatorio de Equipamentos",
        model=Equipment,
        columns=(
            ReportColumnSpec("category", "Categoria", lambda item: item.category),
            ReportColumnSpec("brand", "Marca", lambda item: item.brand),
            ReportColumnSpec("model", "Modelo", lambda item: item.model),
            ReportColumnSpec("serial_number", "Serie", lambda item: item.serial_number),
            ReportColumnSpec("created_at", "Criado em", lambda item: item.created_at),
        ),
    ),
    "inventory": ReportSpec(
        title="Relatorio de Estoque",
        model=InventoryItem,
        columns=(
            ReportColumnSpec("sku", "SKU", lambda item: item.sku),
            ReportColumnSpec("name", "Nome", lambda item: item.name),
            ReportColumnSpec("category", "Categoria", lambda item: item.category),
            ReportColumnSpec("quantity", "Quantidade", lambda item: item.quantity),
            ReportColumnSpec("minimum_quantity", "Minimo", lambda item: item.minimum_quantity),
            ReportColumnSpec("unit_cost", "Custo", lambda item: item.unit_cost),
        ),
    ),
    "service_orders": ReportSpec(
        title="Relatorio de Ordens de Servico",
        model=ServiceOrder,
        columns=(
            ReportColumnSpec("code", "Codigo", lambda item: item.code),
            ReportColumnSpec("status", "Status", lambda item: item.status),
            ReportColumnSpec("problem_description", "Problema", lambda item: item.problem_description),
            ReportColumnSpec("quoted_total", "Total", lambda item: item.quoted_total),
            ReportColumnSpec("created_at", "Criada em", lambda item: item.created_at),
            ReportColumnSpec("closed_at", "Encerrada em", lambda item: item.closed_at),
        ),
    ),
    "users": ReportSpec(
        title="Relatorio de Usuarios",
        model=User,
        columns=(
            ReportColumnSpec("full_name", "Nome", lambda item: item.full_name),
            ReportColumnSpec("email", "Email", lambda item: item.email),
            ReportColumnSpec("role", "Perfil", lambda item: item.role),
            ReportColumnSpec("is_active", "Ativo", lambda item: item.is_active),
            ReportColumnSpec(
                "must_change_password",
                "Troca senha",
                lambda item: item.must_change_password,
            ),
        ),
    ),
}


def build_report(db: Session, company_id, module_key: str) -> dict[str, Any]:
    spec = _get_report_spec(module_key)
    statement = (
        select(spec.model)
        .where(spec.model.company_id == company_id)
        .order_by(spec.model.created_at.desc())
    )
    records = list(db.scalars(statement))
    rows = [
        {
            column.key: _serialize_value(column.getter(record))
            for column in spec.columns
        }
        for record in records
    ]
    return {
        "module": module_key,
        "title": spec.title,
        "generated_at": datetime.now(UTC),
        "total_records": len(rows),
        "columns": [{"key": column.key, "label": column.label} for column in spec.columns],
        "rows": rows,
    }


def export_report(report: dict[str, Any], report_format: str) -> tuple[bytes, str, str]:
    module_key = str(report["module"])
    generated_at = report["generated_at"]
    if isinstance(generated_at, datetime):
        timestamp = generated_at.strftime("%Y%m%d_%H%M%S")
    else:
        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")

    if report_format == "csv":
        return (
            _export_csv(report),
            "text/csv; charset=utf-8",
            f"{module_key}_{timestamp}.csv",
        )
    if report_format == "xlsx":
        return (
            _export_xlsx(report),
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            f"{module_key}_{timestamp}.xlsx",
        )
    if report_format == "pdf":
        return (
            _export_pdf(report),
            "application/pdf",
            f"{module_key}_{timestamp}.pdf",
        )

    raise ValueError("Unsupported report format.")


def _export_csv(report: dict[str, Any]) -> bytes:
    output = StringIO()
    writer = csv.writer(output, delimiter=";")
    columns = report["columns"]
    writer.writerow([column["label"] for column in columns])
    for row in report["rows"]:
        writer.writerow([row.get(column["key"], "") for column in columns])

    return output.getvalue().encode("utf-8-sig")


def _export_xlsx(report: dict[str, Any]) -> bytes:
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Relatorio"
    columns = report["columns"]
    worksheet.append([column["label"] for column in columns])
    for row in report["rows"]:
        worksheet.append([row.get(column["key"], "") for column in columns])

    for column_cells in worksheet.columns:
        max_length = max(len(str(cell.value or "")) for cell in column_cells)
        worksheet.column_dimensions[column_cells[0].column_letter].width = min(max_length + 2, 48)

    output = BytesIO()
    workbook.save(output)
    return output.getvalue()


def _export_pdf(report: dict[str, Any]) -> bytes:
    output = BytesIO()
    document = SimpleDocTemplate(output, pagesize=landscape(A4))
    styles = getSampleStyleSheet()
    columns = report["columns"]
    table_data = [[column["label"] for column in columns]]
    for row in report["rows"]:
        table_data.append([str(row.get(column["key"], ""))[:80] for column in columns])

    table = Table(table_data, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#edf3fb")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#172033")),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#d8e0ea")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    elements = [
        Paragraph(str(report["title"]), styles["Title"]),
        Paragraph(f"Total de registros: {report['total_records']}", styles["Normal"]),
        Spacer(1, 12),
        table,
    ]
    document.build(elements)
    return output.getvalue()


def _get_report_spec(module_key: str) -> ReportSpec:
    try:
        return REPORT_SPECS[module_key]
    except KeyError as exc:
        raise ValueError("Unsupported report module.") from exc


def _serialize_value(value: Any) -> Any:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "Sim" if value else "Nao"
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    if hasattr(value, "value"):
        return value.value
    return str(value)
