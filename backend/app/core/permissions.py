from __future__ import annotations

from backend.app.models.enums import UserRole


ROLE_PERMISSIONS: dict[UserRole, tuple[str, ...]] = {
    UserRole.ADMIN: (
        "dashboard:view",
        "service_orders:*",
        "customers:*",
        "equipment:*",
        "inventory:*",
        "financial:*",
        "reports:*",
        "users:*",
        "sectors:*",
        "settings:*",
        "audit_logs:view",
        "notifications:view",
    ),
    UserRole.MANAGER: (
        "dashboard:view",
        "service_orders:*",
        "customers:*",
        "equipment:*",
        "inventory:*",
        "financial:*",
        "reports:view",
        "users:sector",
        "sectors:view",
        "password_resets:resolve",
        "notifications:view",
    ),
    UserRole.TECHNICIAN: (
        "dashboard:view",
        "service_orders:assigned",
        "customers:view",
        "equipment:view",
        "inventory:view",
    ),
    UserRole.CUSTOMER: (
        "customer_portal:view",
        "customer_portal:quote_decision",
    ),
}


def permissions_for_role(role: UserRole) -> list[str]:
    return list(ROLE_PERMISSIONS.get(role, ()))
