from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.api.dependencies import require_roles
from backend.app.db.session import get_db
from backend.app.models.enums import UserRole
from backend.app.models.password_reset import PasswordResetRequest
from backend.app.models.user import User
from backend.app.schemas.password_reset import (
    PasswordResetRequestResponse,
    PasswordResetResolveRequest,
)
from backend.app.services.password_resets import (
    cancel_password_reset_request,
    get_password_reset_request,
    list_password_reset_requests,
    resolve_password_reset_request,
)

router = APIRouter(prefix="/password-reset-requests", tags=["password-reset-requests"])
admin_or_manager_user = require_roles(UserRole.ADMIN, UserRole.MANAGER)


@router.get("", response_model=list[PasswordResetRequestResponse])
def list_password_reset_request_records(
    current_user: User = Depends(admin_or_manager_user),
    db: Session = Depends(get_db),
) -> list[PasswordResetRequest]:
    return list_password_reset_requests(db, current_user)


@router.post("/{request_id}/resolve", response_model=PasswordResetRequestResponse)
def resolve_password_reset_request_record(
    request_id: uuid.UUID,
    payload: PasswordResetResolveRequest,
    current_user: User = Depends(admin_or_manager_user),
    db: Session = Depends(get_db),
) -> PasswordResetRequest:
    request = get_password_reset_request(db, current_user.company_id, request_id)
    if request is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Password reset request not found.",
        )

    try:
        return resolve_password_reset_request(db, current_user, request, payload.new_password)
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/{request_id}/cancel", response_model=PasswordResetRequestResponse)
def cancel_password_reset_request_record(
    request_id: uuid.UUID,
    current_user: User = Depends(admin_or_manager_user),
    db: Session = Depends(get_db),
) -> PasswordResetRequest:
    request = get_password_reset_request(db, current_user.company_id, request_id)
    if request is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Password reset request not found.",
        )

    try:
        return cancel_password_reset_request(db, current_user, request)
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
