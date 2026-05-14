from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.api.dependencies import require_roles
from backend.app.db.session import get_db
from backend.app.models.enums import UserRole
from backend.app.models.user import User
from backend.app.schemas.user import (
    UserCreate,
    UserPasswordReset,
    UserResponse,
    UserSummaryResponse,
    UserUpdate,
)
from backend.app.services.users import (
    create_user_account,
    get_company_user,
    list_company_users,
    list_users_by_role,
    reset_user_password,
    update_user_account,
)

router = APIRouter(prefix="/users", tags=["users"])
staff_user = require_roles(UserRole.ADMIN, UserRole.MANAGER, UserRole.TECHNICIAN)
admin_or_manager_user = require_roles(UserRole.ADMIN, UserRole.MANAGER)
admin_user = require_roles(UserRole.ADMIN)


def _validate_manager_scope(current_user: User, role: UserRole | None) -> None:
    if current_user.role == UserRole.MANAGER and role not in {None, UserRole.TECHNICIAN}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Managers can only manage technician users in this MVP.",
        )


@router.get("", response_model=list[UserResponse])
def list_user_records(
    current_user: User = Depends(admin_or_manager_user),
    db: Session = Depends(get_db),
) -> list[User]:
    users = list_company_users(db, current_user.company_id)
    if current_user.role == UserRole.MANAGER:
        return [user for user in users if user.role == UserRole.TECHNICIAN]

    return users


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user_record(
    payload: UserCreate,
    current_user: User = Depends(admin_or_manager_user),
    db: Session = Depends(get_db),
) -> User:
    _validate_manager_scope(current_user, payload.role)
    try:
        return create_user_account(db, current_user.company_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.patch("/{user_id}", response_model=UserResponse)
def update_user_record(
    user_id: uuid.UUID,
    payload: UserUpdate,
    current_user: User = Depends(admin_or_manager_user),
    db: Session = Depends(get_db),
) -> User:
    _validate_manager_scope(current_user, payload.role)
    user = get_company_user(db, current_user.company_id, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    if current_user.role == UserRole.MANAGER and user.role != UserRole.TECHNICIAN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Managers can only manage technician users in this MVP.",
        )

    try:
        return update_user_account(db, current_user.company_id, user, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/{user_id}/reset-password", response_model=UserResponse)
def reset_user_record_password(
    user_id: uuid.UUID,
    payload: UserPasswordReset,
    current_user: User = Depends(admin_user),
    db: Session = Depends(get_db),
) -> User:
    user = get_company_user(db, current_user.company_id, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    return reset_user_password(db, user, payload.new_password)


@router.get("/technicians", response_model=list[UserSummaryResponse])
def list_technicians(
    current_user: User = Depends(staff_user),
    db: Session = Depends(get_db),
) -> list[User]:
    return list_users_by_role(db, current_user.company_id, UserRole.TECHNICIAN)
