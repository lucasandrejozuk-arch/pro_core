from __future__ import annotations

import json
import uuid

from sqlalchemy.orm import Session

from backend.app.models.enums import UserRole
from backend.app.models.user import User
from backend.app.services.configuration import get_setting_value, set_setting_value
from backend.app.services.users import get_company_user, list_company_users

RESOURCE_ACCESS_KEY_PREFIX = "security.user_resource_access"
TOOL_SPECIALTY_KEY_PREFIX = "security.user_tool_specialties"
SYSTEM_RESOURCE_KEYS: tuple[str, ...] = (
    "dashboard",
    "service_orders",
    "customers",
    "equipment",
    "inventory",
    "tools",
    "admin_area",
    "sectors",
    "users",
    "resource_access",
    "password_resets",
    "audit_logs",
    "settings",
)
SYSTEM_TOOL_SPECIALTIES: tuple[str, ...] = (
    "eletrica",
    "operacional",
)

DEFAULT_RESOURCE_ACCESS_BY_ROLE: dict[UserRole, tuple[str, ...]] = {
    UserRole.ADMIN: SYSTEM_RESOURCE_KEYS,
    UserRole.MANAGER: (
        "dashboard",
        "service_orders",
        "customers",
        "equipment",
        "inventory",
        "tools",
        "admin_area",
        "sectors",
        "users",
        "resource_access",
        "password_resets",
    ),
    UserRole.TECHNICIAN: (
        "dashboard",
        "service_orders",
        "equipment",
        "inventory",
        "tools",
    ),
    UserRole.CUSTOMER: (),
}


def get_user_resource_access(db: Session, user: User) -> list[str]:
    default_resources = set(DEFAULT_RESOURCE_ACCESS_BY_ROLE.get(user.role, ()))
    if not default_resources:
        return []
    setting_key = _resource_access_setting_key(user.id)
    raw = get_setting_value(db, user.company_id, setting_key)
    if not raw:
        return sorted(default_resources)

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return sorted(default_resources)

    if not isinstance(parsed, list):
        return sorted(default_resources)

    allowed = {str(item or "").strip() for item in parsed if str(item or "").strip()}
    effective = sorted(default_resources & allowed)
    return effective


def get_user_tool_specialties(db: Session, user: User) -> list[str]:
    if "tools" not in set(DEFAULT_RESOURCE_ACCESS_BY_ROLE.get(user.role, ())):
        return []

    setting_key = _tool_specialty_setting_key(user.id)
    raw = get_setting_value(db, user.company_id, setting_key)
    if not raw:
        return list(SYSTEM_TOOL_SPECIALTIES)

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return list(SYSTEM_TOOL_SPECIALTIES)

    if not isinstance(parsed, list):
        return list(SYSTEM_TOOL_SPECIALTIES)

    allowed = {str(item or "").strip().lower() for item in parsed if str(item or "").strip()}
    return sorted(set(SYSTEM_TOOL_SPECIALTIES) & allowed)


def list_manageable_resource_access_users(db: Session, current_user: User) -> list[dict]:
    users = list_company_users(db, current_user.company_id)
    manageable = [user for user in users if _can_manage_resource_access(current_user, user)]
    records: list[dict] = []
    for user in manageable:
        default_resources = sorted(DEFAULT_RESOURCE_ACCESS_BY_ROLE.get(user.role, ()))
        records.append(
            {
                "user_id": user.id,
                "full_name": user.full_name,
                "email": user.email,
                "role": user.role,
                "sector_id": user.sector_id,
                "sector_name": user.sector_name,
                "allowed_resources": get_user_resource_access(db, user),
                "default_resources": default_resources,
                "allowed_tool_specialties": get_user_tool_specialties(db, user),
                "default_tool_specialties": list(SYSTEM_TOOL_SPECIALTIES),
            }
        )
    return records


def update_user_resource_access(
    db: Session,
    current_user: User,
    target_user_id: uuid.UUID,
    allowed_resources: list[str],
    allowed_tool_specialties: list[str] | None = None,
) -> dict:
    target_user = get_company_user(db, current_user.company_id, target_user_id)
    if target_user is None:
        raise ValueError("User not found.")
    if not _can_manage_resource_access(current_user, target_user):
        raise PermissionError(
            "Managers can only manage resource access for technicians in their own sector."
        )

    default_resources = set(DEFAULT_RESOURCE_ACCESS_BY_ROLE.get(target_user.role, ()))
    requested = {str(item or "").strip() for item in allowed_resources if str(item or "").strip()}
    if not requested.issubset(default_resources):
        raise ValueError("Requested resources exceed role default permissions.")

    normalized = sorted(requested)
    set_setting_value(
        db,
        current_user.company_id,
        _resource_access_setting_key(target_user.id),
        json.dumps(normalized, ensure_ascii=True),
        "Recursos liberados para o usuario no sistema.",
    )

    normalized_specialties: list[str]
    if "tools" not in requested:
        normalized_specialties = []
    elif allowed_tool_specialties is None:
        normalized_specialties = get_user_tool_specialties(db, target_user)
    else:
        requested_specialties = {
            str(item or "").strip().lower()
            for item in allowed_tool_specialties
            if str(item or "").strip()
        }
        if not requested_specialties.issubset(set(SYSTEM_TOOL_SPECIALTIES)):
            raise ValueError("Requested tool specialties are invalid.")
        normalized_specialties = sorted(requested_specialties)

    set_setting_value(
        db,
        current_user.company_id,
        _tool_specialty_setting_key(target_user.id),
        json.dumps(normalized_specialties, ensure_ascii=True),
        "Especialidades de ferramentas liberadas para o usuario.",
    )

    db.commit()
    return {
        "user_id": target_user.id,
        "full_name": target_user.full_name,
        "email": target_user.email,
        "role": target_user.role,
        "sector_id": target_user.sector_id,
        "sector_name": target_user.sector_name,
        "allowed_resources": normalized,
        "default_resources": sorted(default_resources),
        "allowed_tool_specialties": normalized_specialties,
        "default_tool_specialties": list(SYSTEM_TOOL_SPECIALTIES),
    }


def _can_manage_resource_access(current_user: User, target_user: User) -> bool:
    if current_user.role == UserRole.ADMIN:
        return target_user.role != UserRole.CUSTOMER
    if current_user.role != UserRole.MANAGER:
        return False
    if current_user.sector_id is None:
        return False
    return (
        target_user.role == UserRole.TECHNICIAN and target_user.sector_id == current_user.sector_id
    )


def _resource_access_setting_key(user_id: uuid.UUID) -> str:
    return f"{RESOURCE_ACCESS_KEY_PREFIX}.{user_id}"


def _tool_specialty_setting_key(user_id: uuid.UUID) -> str:
    return f"{TOOL_SPECIALTY_KEY_PREFIX}.{user_id}"
