from __future__ import annotations

from frontend.app.screens.dashboard_mixins_4_audit import DashboardAuditMixin
from frontend.app.screens.dashboard_mixins_4_settings_admin import DashboardSettingsAdminMixin


class DashboardMixin4(
    DashboardSettingsAdminMixin,
    DashboardAuditMixin,
):
    pass
