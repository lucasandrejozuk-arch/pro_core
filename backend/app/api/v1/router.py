from fastapi import APIRouter

from backend.app.api.v1.routes import (
    audit,
    auth,
    customer_portal,
    customers,
    documents,
    equipment,
    financial,
    inventory,
    notifications,
    password_resets,
    reports,
    sectors,
    service_orders,
    settings,
    users,
)

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(audit.router)
api_router.include_router(auth.router)
api_router.include_router(customer_portal.router)
api_router.include_router(customers.router)
api_router.include_router(documents.router)
api_router.include_router(equipment.router)
api_router.include_router(financial.router)
api_router.include_router(inventory.router)
api_router.include_router(notifications.router)
api_router.include_router(password_resets.router)
api_router.include_router(reports.router)
api_router.include_router(sectors.router)
api_router.include_router(service_orders.router)
api_router.include_router(settings.router)
api_router.include_router(users.router)
