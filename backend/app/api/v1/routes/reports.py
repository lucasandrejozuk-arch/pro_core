from __future__ import annotations

from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from backend.app.api.dependencies import require_roles
from backend.app.db.session import get_db
from backend.app.models.enums import UserRole
from backend.app.models.user import User
from backend.app.schemas.report import ReportFormat, ReportModule, ReportResponse
from backend.app.services.reports import build_report, export_report

router = APIRouter(prefix="/reports", tags=["reports"])
admin_user = require_roles(UserRole.ADMIN)


@router.get("/{module_key}", response_model=ReportResponse)
def get_report(
    module_key: ReportModule,
    current_user: User = Depends(admin_user),
    db: Session = Depends(get_db),
) -> ReportResponse:
    try:
        return build_report(db, current_user.company_id, module_key)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/{module_key}/export")
def export_report_file(
    module_key: ReportModule,
    report_format: ReportFormat = Query(alias="format"),
    current_user: User = Depends(admin_user),
    db: Session = Depends(get_db),
) -> StreamingResponse:
    try:
        report = build_report(db, current_user.company_id, module_key)
        content, media_type, file_name = export_report(report, report_format)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return StreamingResponse(
        BytesIO(content),
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{file_name}"'},
    )
