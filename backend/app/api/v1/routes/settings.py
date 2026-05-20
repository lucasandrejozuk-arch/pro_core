from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.api.dependencies import get_current_user, require_roles
from backend.app.db.session import get_db
from backend.app.models.enums import UserRole
from backend.app.models.user import User
from backend.app.schemas.configuration import (
    AppearanceSettingsResponse,
    BackupRunResponse,
    SystemSettingsResponse,
    SystemSettingsUpdate,
)
from backend.app.services.backup import run_database_backup
from backend.app.services.configuration import (
    get_appearance_settings,
    get_login_appearance_settings,
    get_system_settings,
    update_system_settings,
)

router = APIRouter(prefix="/settings", tags=["settings"])
admin_user = require_roles(UserRole.ADMIN)
CurrentUser = Annotated[User, Depends(get_current_user)]
AdminUser = Annotated[User, Depends(admin_user)]
DatabaseSession = Annotated[Session, Depends(get_db)]


@router.get("/appearance", response_model=AppearanceSettingsResponse)
def get_appearance(
    current_user: CurrentUser,
    db: DatabaseSession,
) -> AppearanceSettingsResponse:
    try:
        return get_appearance_settings(db, current_user.company_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/login-appearance", response_model=AppearanceSettingsResponse)
def get_login_appearance(db: DatabaseSession) -> AppearanceSettingsResponse:
    return get_login_appearance_settings(db)


@router.get("", response_model=SystemSettingsResponse)
def get_settings(
    current_user: AdminUser,
    db: DatabaseSession,
) -> SystemSettingsResponse:
    try:
        return get_system_settings(db, current_user.company_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.patch("", response_model=SystemSettingsResponse)
def update_settings(
    payload: SystemSettingsUpdate,
    current_user: AdminUser,
    db: DatabaseSession,
) -> SystemSettingsResponse:
    try:
        return update_system_settings(db, current_user.company_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/backup/run", response_model=BackupRunResponse)
def run_backup(
    current_user: AdminUser,
    db: DatabaseSession,
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
