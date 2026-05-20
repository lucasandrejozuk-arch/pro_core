from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.api.dependencies import require_roles
from backend.app.db.session import get_db
from backend.app.models.enums import UserRole
from backend.app.models.user import User
from backend.app.schemas.audit import AuditLogResponse
from backend.app.services.audit import delete_audit_log, list_audit_logs

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


@router.delete("/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_audit_log_record(
    log_id: uuid.UUID,
    current_user: User = Depends(admin_user),
    db: Session = Depends(get_db),
) -> None:
    deleted = delete_audit_log(db, current_user.company_id, log_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audit log not found.")
