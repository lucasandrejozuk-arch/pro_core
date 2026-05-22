from __future__ import annotations

from frontend.app.screens.dashboard_mixins_1_layout import DashboardLayoutMixin
from frontend.app.screens.dashboard_mixins_1_status import DashboardStatusMixin


class DashboardMixin1(
    DashboardLayoutMixin,
    DashboardStatusMixin,
):
    pass
