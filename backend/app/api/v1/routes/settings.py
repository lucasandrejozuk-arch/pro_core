from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.api.dependencies import require_roles
from backend.app.db.session import get_db
from backend.app.models.enums import UserRole
from backend.app.models.user import User
from backend.app.schemas.configuration import (
    BackupRunResponse,
    SystemSettingsResponse,
    SystemSettingsUpdate,
)
from backend.app.services.backup import run_database_backup
from backend.app.services.configuration import get_system_settings, update_system_settings

router = APIRouter(prefix="/settings", tags=["settings"])
admin_user = require_roles(UserRole.ADMIN)


@router.get("", response_model=SystemSettingsResponse)
def get_settings(
    current_user: User = Depends(admin_user),
    db: Session = Depends(get_db),
) -> SystemSettingsResponse:
    try:
        return get_system_settings(db, current_user.company_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.patch("", response_model=SystemSettingsResponse)
def update_settings(
    payload: SystemSettingsUpdate,
    current_user: User = Depends(admin_user),
    db: Session = Depends(get_db),
) -> SystemSettingsResponse:
    try:
        return update_system_settings(db, current_user.company_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/backup/run", response_model=BackupRunResponse)
def run_backup(
    current_user: User = Depends(admin_user),
    db: Session = Depends(get_db),
) -> BackupRunResponse:
    try:
        return run_database_backup(db, current_user.company_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc
