from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.security import (
    hash_password,
    validate_password_strength,
    verify_password,
    verify_password_for_missing_user,
)
from backend.app.models.enums import UserRole
from backend.app.models.user import User
from backend.app.schemas.user import UserCreate, UserUpdate
from backend.app.services.crud import apply_updates
from backend.app.services.sectors import get_or_create_admin_sector, get_sector


def normalize_email(email: str) -> str:
    return email.strip().lower()


def get_user_by_id(db: Session, user_id: uuid.UUID) -> User | None:
    return db.get(User, user_id)


def get_user_by_email(db: Session, email: str) -> User | None:
    statement = select(User).where(User.email == normalize_email(email))
    return db.scalars(statement).first()


def get_company_user(db: Session, company_id: uuid.UUID, user_id: uuid.UUID) -> User | None:
    statement = select(User).where(
        User.id == user_id,
        User.company_id == company_id,
    )
    return db.scalars(statement).first()


def get_company_user_by_email(db: Session, company_id: uuid.UUID, email: str) -> User | None:
    statement = select(User).where(
        User.company_id == company_id,
        User.email == normalize_email(email),
    )
    return db.scalars(statement).first()


def list_company_users(
    db: Session,
    company_id: uuid.UUID,
    sector_id: uuid.UUID | None = None,
    role: UserRole | None = None,
) -> list[User]:
    filters = [User.company_id == company_id]
    if sector_id is not None:
        filters.append(User.sector_id == sector_id)
    if role is not None:
        filters.append(User.role == role)

    statement = select(User).where(*filters).order_by(User.full_name)
    return list(db.scalars(statement))


def list_users_by_role(
    db: Session,
    company_id: uuid.UUID,
    role: UserRole,
    sector_id: uuid.UUID | None = None,
) -> list[User]:
    filters = [
        User.company_id == company_id,
        User.role == role,
        User.is_active.is_(True),
    ]
    if sector_id is not None:
        filters.append(User.sector_id == sector_id)

    statement = select(User).where(*filters).order_by(User.full_name)
    return list(db.scalars(statement))


def create_user_account(db: Session, company_id: uuid.UUID, payload: UserCreate) -> User:
    if get_company_user_by_email(db, company_id, payload.email):
        raise ValueError("Email already registered for this company.")

    sector_id = payload.sector_id
    if payload.role == UserRole.ADMIN and sector_id is None:
        sector_id = get_or_create_admin_sector(db, company_id).id

    _validate_user_sector(db, company_id, sector_id)
    validate_password_strength(payload.password)

    user = User(
        company_id=company_id,
        sector_id=sector_id,
        full_name=payload.full_name,
        email=normalize_email(payload.email),
        password_hash=hash_password(payload.password),
        role=payload.role,
        is_active=True,
        must_change_password=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user_account(
    db: Session,
    company_id: uuid.UUID,
    user: User,
    payload: UserUpdate,
) -> User:
    update_data = payload.model_dump(exclude_unset=True)
    new_email = update_data.get("email")
    if new_email:
        existing_user = get_company_user_by_email(db, company_id, new_email)
        if existing_user and existing_user.id != user.id:
            raise ValueError("Email already registered for this company.")

    if "sector_id" in update_data:
        _validate_user_sector(db, company_id, update_data["sector_id"])

    apply_updates(user, payload)
    if user.email:
        user.email = normalize_email(user.email)

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _validate_user_sector(
    db: Session,
    company_id: uuid.UUID,
    sector_id: uuid.UUID | None,
) -> None:
    if sector_id is None:
        return

    if get_sector(db, company_id, sector_id) is None:
        raise ValueError("Sector not found for this company.")


def reset_user_password(
    db: Session,
    user: User,
    new_password: str,
    *,
    validate_strength: bool = True,
) -> User:
    if validate_strength:
        validate_password_strength(new_password)
    user.password_hash = hash_password(new_password)
    user.must_change_password = True
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = get_user_by_email(db, email)
    if user is None or not user.is_active:
        verify_password_for_missing_user(password)
        return None

    if not verify_password(password, user.password_hash):
        return None

    return user


def change_user_password(db: Session, user: User, current_password: str, new_password: str) -> User:
    if not verify_password(current_password, user.password_hash):
        raise ValueError("Current password is invalid.")

    if verify_password(new_password, user.password_hash):
        raise ValueError("New password must be different from the current password.")

    validate_password_strength(new_password)
    user.password_hash = hash_password(new_password)
    user.must_change_password = False
    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def delete_user_account(db: Session, company_id: uuid.UUID, user: User, actor: User) -> None:
    if user.company_id != company_id:
        raise ValueError("User not found for this company.")
    if user.id == actor.id:
        raise ValueError("Current user cannot delete own account.")
    if user.role == UserRole.ADMIN:
        admins = list_company_users(db, company_id=company_id, role=UserRole.ADMIN)
        if len(admins) <= 1:
            raise ValueError("At least one admin account must remain active.")

    db.delete(user)
    db.commit()
