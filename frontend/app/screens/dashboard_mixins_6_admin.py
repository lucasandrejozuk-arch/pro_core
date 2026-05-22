from __future__ import annotations

from frontend.app.screens.dashboard_mixins_6_admin_accounts import (
    DashboardAdminAccountActionsMixin,
)
from frontend.app.screens.dashboard_mixins_6_admin_settings import (
    DashboardAdminSettingsActionsMixin,
)


class DashboardAdminActionsMixin(
    DashboardAdminAccountActionsMixin,
    DashboardAdminSettingsActionsMixin,
):
    pass
