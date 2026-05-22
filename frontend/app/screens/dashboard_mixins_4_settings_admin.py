from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QVBoxLayout

from frontend.app.core.grid import GRID_COLUMNS, create_grid
from frontend.app.screens.dashboard_mixins_4_settings_form import DashboardSettingsFormMixin


class DashboardSettingsAdminMixin(DashboardSettingsFormMixin):

    def _build_admin_area_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("formPanel")
        title = QLabel("AREA ADMINISTRATIVA")
        title.setObjectName("sectionTitle")
        description = QLabel("Usuarios, setores, solicitacoes de senha e logs de auditoria.")
        description.setObjectName("mutedText")
        description.setWordWrap(True)
        header = QFrame()
        header.setObjectName("adminAreaHeader")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(4)
        header_layout.addWidget(title)
        header_layout.addWidget(description)
        self.admin_area_status_label = QLabel(
            "Selecione uma etapa administrativa liberada para o seu perfil."
        )
        self.admin_area_status_label.setObjectName("statusBanner")
        self.admin_area_status_label.setProperty("level", "warning")
        self.admin_area_status_label.setWordWrap(True)
        self.admin_area_status_label.setMaximumHeight(42)
        self.admin_area_scope_label = QLabel("Modulos administrativos disponiveis: carregando.")
        self.admin_area_scope_label.setObjectName("moduleActionHint")
        self.admin_area_scope_label.setWordWrap(True)
        access_panel = QFrame()
        access_panel.setObjectName("formSubPanel")
        access_layout = QVBoxLayout(access_panel)
        access_layout.setContentsMargins(10, 10, 10, 10)
        access_layout.setSpacing(6)
        access_layout.addWidget(self.admin_area_status_label)
        access_layout.addWidget(self.admin_area_scope_label)
        self.backend_restart_status_label = QLabel(self.backend_restart_message)
        self.backend_restart_status_label.setObjectName("moduleActionHint")
        self.backend_restart_status_label.setWordWrap(True)
        self.backend_restart_button = QPushButton("Reiniciar backend local")
        self.backend_restart_button.setObjectName("secondaryButton")
        self.backend_restart_button.setToolTip(
            "Reinicia somente o backend iniciado pelo proprio app nesta sessao."
        )
        self.backend_restart_button.clicked.connect(self.backend_restart_requested.emit)
        backend_actions = QHBoxLayout()
        backend_actions.setContentsMargins(10, 10, 10, 10)
        backend_actions.setSpacing(8)
        backend_actions.addWidget(self.backend_restart_status_label, 1)
        backend_actions.addWidget(self.backend_restart_button)
        backend_panel = QFrame()
        backend_panel.setObjectName("formSubPanel")
        backend_panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        backend_panel.setLayout(backend_actions)
        actions_title = QLabel("ATALHOS ADMINISTRATIVOS")
        actions_title.setObjectName("formGroupTitle")
        self.admin_area_actions_layout = create_grid(spacing=10, margins=(0, 0, 0, 0))
        self.admin_area_actions_panel = QFrame()
        self.admin_area_actions_panel.setObjectName("formSubPanel")
        actions_panel_layout = QVBoxLayout(self.admin_area_actions_panel)
        actions_panel_layout.setContentsMargins(10, 10, 10, 10)
        actions_panel_layout.setSpacing(8)
        actions_panel_layout.addWidget(actions_title)
        actions_panel_layout.addLayout(self.admin_area_actions_layout)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(header)
        layout.addWidget(access_panel)
        layout.addWidget(backend_panel)
        layout.addWidget(self.admin_area_actions_panel)
        self._sync_backend_restart_control()
        return panel

    def render_admin_area(self) -> None:
        self._set_active_module("admin_area")
        self._clear_layout(self.admin_area_actions_layout)
        allowed_modules = [
            module_key
            for module_key in self._allowed_admin_modules()
            if module_key
            in {"sectors", "users", "resource_access", "password_resets", "audit_logs"}
        ]
        self.admin_area_scope_label.setText(self._format_admin_area_scope(allowed_modules))
        self._sync_backend_restart_control()
        if not allowed_modules:
            self._set_admin_area_status(
                "Seu perfil nao possui acesso a area administrativa.", "error"
            )
            label = QLabel("Seu perfil nao possui acesso a area administrativa.")
            label.setObjectName("mutedText")
            self.admin_area_actions_layout.addWidget(label, 0, 0, 1, GRID_COLUMNS)
            return
        role_name = "Administrador" if self.current_user_role == "admin" else "Gestor"
        self._set_admin_area_status(
            f"{role_name}: {len(allowed_modules)} modulo(s) administrativo(s) liberado(s).",
            "info",
        )
        start_index = 0
        if self.current_user_role == "admin":
            portal_button = QPushButton("Portal do cliente (navegador)")
            portal_button.setObjectName("adminMenuButton")
            portal_button.setCursor(Qt.CursorShape.PointingHandCursor)
            portal_button.clicked.connect(self.customer_portal_open_requested.emit)
            self.admin_area_actions_layout.addWidget(portal_button, 0, 0, 1, GRID_COLUMNS)
            start_index = 1
        for index, module_key in enumerate(allowed_modules):
            button = QPushButton(self.module_labels[module_key])
            button.setObjectName("adminMenuButton")
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.clicked.connect(
                lambda checked=False, key=module_key: self.module_selected.emit(key)
            )
            absolute_index = index + start_index
            row = absolute_index // 2
            column = (absolute_index % 2) * 6
            self.admin_area_actions_layout.addWidget(button, row, column, 1, 6)

    def _set_admin_area_status(self, message: str, level: str) -> None:
        self.admin_area_status_label.setText(message)
        self.admin_area_status_label.setProperty("level", level)
        self.admin_area_status_label.style().unpolish(self.admin_area_status_label)
        self.admin_area_status_label.style().polish(self.admin_area_status_label)

    def _format_admin_area_scope(self, allowed_modules: list[str]) -> str:
        if not allowed_modules:
            return "Modulos administrativos disponiveis: nenhum para o perfil atual."
        modules = [self.module_labels[module_key] for module_key in allowed_modules]
        return "Modulos administrativos disponiveis: " + " | ".join(modules)

    def set_backend_restart_available(self, is_available: bool, message: str = "") -> None:
        self.backend_restart_available = is_available
        if message:
            self.backend_restart_message = message
        elif is_available:
            self.backend_restart_message = (
                "Reinicio seguro disponivel: backend gerenciado pelo app."
            )
        else:
            self.backend_restart_message = (
                "Reinicio seguro indisponivel: backend atual nao foi iniciado pelo app."
            )
        self._sync_backend_restart_control()

    def set_backend_restart_loading(self, is_loading: bool) -> None:
        self.backend_restart_in_progress = is_loading
        self._sync_backend_restart_control()

    def _sync_backend_restart_control(self) -> None:
        if not hasattr(self, "backend_restart_button"):
            return
        is_admin = self.current_user_role == "admin"
        if not is_admin:
            status = "Reinicio do backend restrito a administradores."
        else:
            status = self.backend_restart_message
        can_click = (
            is_admin and self.backend_restart_available and not self.backend_restart_in_progress
        )
        self.backend_restart_button.setEnabled(can_click)
        self.backend_restart_button.setText(
            "Reiniciando..." if self.backend_restart_in_progress else "Reiniciar backend local"
        )
        self.backend_restart_status_label.setText(status)
