from __future__ import annotations

from frontend.app.core.api_admin_settings import AdminSettingsApiMixin
from frontend.app.core.api_auth import AuthApiMixin
from frontend.app.core.api_customers_equipment import CustomerEquipmentApiMixin
from frontend.app.core.api_errors import ApiError
from frontend.app.core.api_inventory_service_orders import InventoryServiceOrderApiMixin
from frontend.app.core.api_transport import ApiTransportMixin

__all__ = ["ApiClient", "ApiError"]


class ApiClient(
    AuthApiMixin,
    CustomerEquipmentApiMixin,
    InventoryServiceOrderApiMixin,
    AdminSettingsApiMixin,
    ApiTransportMixin,
):
    pass
