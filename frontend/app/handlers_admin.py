from __future__ import annotations

from PySide6.QtWidgets import QApplication

from frontend.app.handlers_admin_backend_restart import AdminBackendRestartHandlersMixin
from frontend.app.handlers_admin_operations import AdminOperationsHandlersMixin

__all__ = ["AdminHandlersMixin", "QApplication"]


class AdminHandlersMixin(
    AdminBackendRestartHandlersMixin,
    AdminOperationsHandlersMixin,
):
    pass
