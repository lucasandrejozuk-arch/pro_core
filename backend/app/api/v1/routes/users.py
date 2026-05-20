from __future__ import annotations

import uuid
from typing import Annotated

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
StaffUser = Annotated[User, Depends(staff_user)]
AdminOrManagerUser = Annotated[User, Depends(admin_or_manager_user)]
AdminUser = Annotated[User, Depends(admin_user)]
DatabaseSession = Annotated[Session, Depends(get_db)]


def _require_manager_sector(current_user: User) -> uuid.UUID:
    if current_user.sector_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Managers must belong to a sector to manage users.",
        )

    return current_user.sector_id


def _scope_manager_create_payload(current_user: User, payload: UserCreate) -> UserCreate:
    if current_user.role != UserRole.MANAGER:
        return payload

    manager_sector_id = _require_manager_sector(current_user)
    if payload.role != UserRole.TECHNICIAN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Managers can only create technician users in their own sector.",
        )

    return payload.model_copy(update={"sector_id": manager_sector_id})


def _validate_manager_update_scope(
    current_user: User,
    user: User,
    payload: UserUpdate,
) -> None:
    if current_user.role != UserRole.MANAGER:
        return

    manager_sector_id = _require_manager_sector(current_user)
    if user.role != UserRole.TECHNICIAN or user.sector_id != manager_sector_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Managers can only manage technician users in their own sector.",
        )

    update_data = payload.model_dump(exclude_unset=True)
    if update_data.get("role") not in {None, UserRole.TECHNICIAN}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Managers can only manage technician users in their own sector.",
        )

    if "sector_id" in update_data and update_data["sector_id"] != manager_sector_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Managers can only manage technician users in their own sector.",
        )


@router.get("", response_model=list[UserResponse])
def list_user_records(
    current_user: AdminOrManagerUser,
    db: DatabaseSession,
) -> list[User]:
    if current_user.role == UserRole.MANAGER:
        if current_user.sector_id is None:
            return []
        return list_company_users(
            db,
            current_user.company_id,
            sector_id=current_user.sector_id,
            role=UserRole.TECHNICIAN,
        )

    return list_company_users(db, current_user.company_id)


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user_record(
    payload: UserCreate,
    current_user: AdminOrManagerUser,
    db: DatabaseSession,
) -> User:
    payload = _scope_manager_create_payload(current_user, payload)
    try:
        return create_user_account(db, current_user.company_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.patch("/{user_id}", response_model=UserResponse)
def update_user_record(
    user_id: uuid.UUID,
    payload: UserUpdate,
    current_user: AdminOrManagerUser,
    db: DatabaseSession,
) -> User:
    user = get_company_user(db, current_user.company_id, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    _validate_manager_update_scope(current_user, user, payload)

    try:
        return update_user_account(db, current_user.company_id, user, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/{user_id}/reset-password", response_model=UserResponse)
def reset_user_record_password(
    user_id: uuid.UUID,
    payload: UserPasswordReset,
    current_user: AdminUser,
    db: DatabaseSession,
) -> User:
    user = get_company_user(db, current_user.company_id, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    try:
        return reset_user_password(db, user, payload.new_password)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/technicians", response_model=list[UserSummaryResponse])
def list_technicians(
    current_user: StaffUser,
    db: DatabaseSession,
) -> list[User]:
    if current_user.role in {UserRole.MANAGER, UserRole.TECHNICIAN}:
        if current_user.sector_id is None:
            return []
        return list_users_by_role(
            db,
            current_user.company_id,
            UserRole.TECHNICIAN,
            sector_id=current_user.sector_id,
        )

    return list_users_by_role(db, current_user.company_id, UserRole.TECHNICIAN)
