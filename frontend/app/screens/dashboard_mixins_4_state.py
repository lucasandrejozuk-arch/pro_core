from __future__ import annotations

from typing import Any

from frontend.app.screens.dashboard_mixins_4_state_admin import DashboardFormStateAdminMixin
from frontend.app.screens.dashboard_mixins_4_state_customer_inventory import (
    DashboardFormStateCustomerInventoryMixin,
)
from frontend.app.screens.dashboard_mixins_4_state_password_reset import (
    DashboardFormStatePasswordResetMixin,
)


def confirm_destructive_action(*args: Any, **kwargs: Any) -> bool:
    from frontend.app.screens import dashboard

    return bool(dashboard.confirm_destructive_action(*args, **kwargs))


class DashboardFormStateMixin(
    DashboardFormStateCustomerInventoryMixin,
    DashboardFormStateAdminMixin,
    DashboardFormStatePasswordResetMixin,
):
    pass
