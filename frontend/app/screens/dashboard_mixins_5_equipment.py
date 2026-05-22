from __future__ import annotations

from frontend.app.screens.dashboard_mixins_5_equipment_actions import (
    DashboardEquipmentActionsMixin,
)
from frontend.app.screens.dashboard_mixins_5_equipment_tables import DashboardEquipmentTablesMixin


class DashboardEquipmentMixin(
    DashboardEquipmentTablesMixin,
    DashboardEquipmentActionsMixin,
):
    pass
