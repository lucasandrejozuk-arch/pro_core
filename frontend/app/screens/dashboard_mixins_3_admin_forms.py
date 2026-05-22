from __future__ import annotations

from frontend.app.screens.dashboard_mixins_3_admin_forms_accounts import (
    DashboardAdminAccountFormsMixin,
)
from frontend.app.screens.dashboard_mixins_3_admin_forms_password_reset import (
    DashboardAdminPasswordResetFormMixin,
)


class DashboardAdminFormsMixin(
    DashboardAdminAccountFormsMixin,
    DashboardAdminPasswordResetFormMixin,
):
    pass
