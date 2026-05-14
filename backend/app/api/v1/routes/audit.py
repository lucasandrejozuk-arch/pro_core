from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.api.dependencies import require_roles
from backend.app.db.session import get_db
from backend.app.models.enums import UserRole
from backend.app.models.user import User
from backend.app.schemas.audit import AuditLogResponse
from backend.app.services.audit import list_audit_logs

router = APIRouter(prefix="/audit-logs", tags=["audit-logs"])
admin_user = require_roles(UserRole.ADMIN)


@router.get("", response_model=list[AuditLogResponse])
def list_audit_log_records(
    entity_type: str | None = None,
    entity_id: str | None = None,
    current_user: User = Depends(admin_user),
    db: Session = Depends(get_db),
) -> list[AuditLogResponse]:
    return list_audit_logs(
        db,
        company_id=current_user.company_id,
        entity_type=entity_type,
        entity_id=entity_id,
    )
