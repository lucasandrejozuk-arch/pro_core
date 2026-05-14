from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel

ReportModule = Literal[
    "customers",
    "equipment",
    "inventory",
    "service_orders",
    "users",
    "financial",
    "audit_logs",
]
ReportFormat = Literal["csv", "xlsx", "pdf"]


class ReportColumn(BaseModel):
    key: str
    label: str


class ReportResponse(BaseModel):
    module: ReportModule
    title: str
    generated_at: datetime
    total_records: int
    columns: list[ReportColumn]
    rows: list[dict[str, Any]]
