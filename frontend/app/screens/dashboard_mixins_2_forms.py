from __future__ import annotations

from frontend.app.screens.dashboard_mixins_2_forms_customer import DashboardCustomerFormMixin
from frontend.app.screens.dashboard_mixins_2_forms_equipment import DashboardEquipmentFormMixin


class DashboardRecordFormsMixin(
    DashboardCustomerFormMixin,
    DashboardEquipmentFormMixin,
):
    pass
