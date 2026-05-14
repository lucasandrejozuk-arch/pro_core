from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.enums import UserRole
from backend.app.models.password_reset import PasswordResetRequest
from backend.app.models.user import User
from backend.app.services.users import (
    get_company_user,
    get_user_by_email,
    list_company_users,
    reset_user_password,
)

PENDING_STATUS = "pending"
RESOLVED_STATUS = "resolved"


def create_password_reset_request(db: Session, email: str) -> PasswordResetRequest | None:
    user = get_user_by_email(db, email)
    if user is None or not user.is_active:
        return None

    existing_request = get_pending_request_for_user(db, user.company_id, user.id)
    if existing_request is not None:
        return existing_request

    recipient_role, recipient_sector_id = _resolve_recipient_scope(db, user)
    request = PasswordResetRequest(
        company_id=user.company_id,
        requester_user_id=user.id,
        requester_email=user.email,
        requester_full_name=user.full_name,
        requester_role=user.role,
        recipient_role=recipient_role,
        recipient_sector_id=recipient_sector_id,
        status=PENDING_STATUS,
    )
    db.add(request)
    db.commit()
    db.refresh(request)
    return request


def get_pending_request_for_user(
    db: Session,
    company_id: uuid.UUID,
    user_id: uuid.UUID,
) -> PasswordResetRequest | None:
    statement = select(PasswordResetRequest).where(
        PasswordResetRequest.company_id == company_id,
        PasswordResetRequest.requester_user_id == user_id,
        PasswordResetRequest.status == PENDING_STATUS,
    )
    return db.scalars(statement).first()


def get_password_reset_request(
    db: Session,
    company_id: uuid.UUID,
    request_id: uuid.UUID,
) -> PasswordResetRequest | None:
    statement = select(PasswordResetRequest).where(
        PasswordResetRequest.id == request_id,
        PasswordResetRequest.company_id == company_id,
    )
    return db.scalars(statement).first()


def list_password_reset_requests(db: Session, current_user: User) -> list[PasswordResetRequest]:
    statement = (
        select(PasswordResetRequest)
        .where(
            PasswordResetRequest.company_id == current_user.company_id,
            PasswordResetRequest.status == PENDING_STATUS,
        )
        .order_by(PasswordResetRequest.created_at.desc())
    )

    if current_user.role == UserRole.MANAGER:
        if current_user.sector_id is None:
            return []
        statement = statement.where(
            PasswordResetRequest.recipient_role == UserRole.MANAGER,
            PasswordResetRequest.recipient_sector_id == current_user.sector_id,
        )

    return list(db.scalars(statement))


def resolve_password_reset_request(
    db: Session,
    current_user: User,
    request: PasswordResetRequest,
    new_password: str,
) -> PasswordResetRequest:
    if request.status != PENDING_STATUS:
        raise ValueError("Password reset request is already resolved.")

    if not can_access_password_reset_request(current_user, request):
        raise PermissionError("Password reset request is outside the current user's scope.")

    requester = get_company_user(db, current_user.company_id, request.requester_user_id)
    if requester is None or not requester.is_active:
        raise ValueError("Requesting user not found.")

    if current_user.role == UserRole.MANAGER:
        if requester.role not in {UserRole.TECHNICIAN, UserRole.CUSTOMER}:
            raise PermissionError("Managers can only resolve requests for operators.")
        if requester.sector_id != current_user.sector_id:
            raise PermissionError("Password reset request is outside the current user's scope.")

    reset_user_password(db, requester, new_password)
    request.status = RESOLVED_STATUS
    request.resolved_by_user_id = current_user.id
    request.resolved_at = datetime.now(UTC)
    db.add(request)
    db.commit()
    db.refresh(request)
    return request


def can_access_password_reset_request(
    current_user: User,
    request: PasswordResetRequest,
) -> bool:
    if current_user.role == UserRole.ADMIN:
        return True

    if current_user.role != UserRole.MANAGER or current_user.sector_id is None:
        return False

    return (
        request.recipient_role == UserRole.MANAGER
        and request.recipient_sector_id == current_user.sector_id
    )


def _resolve_recipient_scope(db: Session, user: User) -> tuple[UserRole, uuid.UUID | None]:
    if user.role in {UserRole.ADMIN, UserRole.MANAGER}:
        return UserRole.ADMIN, None

    if user.sector_id is not None:
        managers = list_company_users(
            db,
            user.company_id,
            sector_id=user.sector_id,
            role=UserRole.MANAGER,
        )
        if managers:
            return UserRole.MANAGER, user.sector_id

    return UserRole.ADMIN, None
