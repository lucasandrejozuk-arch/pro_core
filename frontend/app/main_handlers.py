from __future__ import annotations

from frontend.app.handlers_admin import AdminHandlersMixin
from frontend.app.handlers_customer_inventory import CustomerInventoryHandlersMixin
from frontend.app.handlers_equipment import EquipmentHandlersMixin
from frontend.app.handlers_service_orders import ServiceOrderHandlersMixin


class ProCoreHandlersMixin(
    CustomerInventoryHandlersMixin,
    EquipmentHandlersMixin,
    ServiceOrderHandlersMixin,
    AdminHandlersMixin,
):
    pass
