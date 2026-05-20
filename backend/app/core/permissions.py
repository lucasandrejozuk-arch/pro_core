from __future__ import annotations

from backend.app.models.enums import UserRole

ROLE_PERMISSIONS: dict[UserRole, tuple[str, ...]] = {
    UserRole.ADMIN: (
        "dashboard:view",
        "service_orders:*",
        "customers:*",
        "equipment:*",
        "inventory:*",
        "tools:*",
        "users:*",
        "sectors:*",
        "settings:*",
        "audit_logs:view",
    ),
    UserRole.MANAGER: (
        "dashboard:view",
        "service_orders:*",
        "customers:*",
        "equipment:*",
        "inventory:*",
        "tools:view",
        "users:sector",
        "sectors:view",
        "password_resets:resolve",
    ),
    UserRole.TECHNICIAN: (
        "dashboard:view",
        "service_orders:assigned",
        "equipment:view",
        "inventory:view",
        "tools:view",
    ),
    UserRole.CUSTOMER: (
        "customer_portal:view",
        "customer_portal:quote_decision",
    ),
}


def permissions_for_role(role: UserRole) -> list[str]:
    return list(ROLE_PERMISSIONS.get(role, ()))
