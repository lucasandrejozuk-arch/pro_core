from __future__ import annotations

from frontend.app.screens.dashboard_mixins_6_inventory import DashboardInventoryActionsMixin
from frontend.app.screens.dashboard_mixins_6_service_orders import (
    DashboardServiceOrderActionsMixin,
)


class DashboardMixin6(
    DashboardInventoryActionsMixin,
    DashboardServiceOrderActionsMixin,
):
    pass
