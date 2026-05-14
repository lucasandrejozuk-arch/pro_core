from fastapi import APIRouter

from backend.app.api.v1.routes import auth, customers, equipment, inventory, service_orders, settings, users

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(customers.router)
api_router.include_router(equipment.router)
api_router.include_router(inventory.router)
api_router.include_router(service_orders.router)
api_router.include_router(settings.router)
api_router.include_router(users.router)
