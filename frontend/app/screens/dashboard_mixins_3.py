from __future__ import annotations

from frontend.app.screens.dashboard_mixins_3_builders import DashboardToolBuilderMixin
from frontend.app.screens.dashboard_mixins_3_calculators import DashboardToolCalculatorMixin


class DashboardMixin3(
    DashboardToolBuilderMixin,
    DashboardToolCalculatorMixin,
):
    pass
