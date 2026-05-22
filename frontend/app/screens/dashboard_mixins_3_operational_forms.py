from __future__ import annotations

from frontend.app.screens.dashboard_mixins_3_operational_forms_inventory import (
    DashboardInventoryFormBuilderMixin,
)
from frontend.app.screens.dashboard_mixins_3_operational_forms_service_orders import (
    DashboardServiceOrderFormBuilderMixin,
)


class DashboardOperationalFormsMixin(
    DashboardInventoryFormBuilderMixin,
    DashboardServiceOrderFormBuilderMixin,
):
    pass
