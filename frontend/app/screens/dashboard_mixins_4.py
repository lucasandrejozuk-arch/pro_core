from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSlider,
    QTabWidget,
    QVBoxLayout,
)

from frontend.app.core.grid import GRID_COLUMNS, create_grid
from frontend.app.widgets import create_summary_text


def confirm_destructive_action(*args: Any, **kwargs: Any) -> bool:
    from frontend.app.screens import dashboard

    return bool(dashboard.confirm_destructive_action(*args, **kwargs))


class DashboardMixin4:
    def _build_settings_form(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("formPanel")

        title = QLabel("CONFIGURACOES DO SISTEMA")
        title.setObjectName("sectionTitle")

        self.settings_company_name_input = QLineEdit()
        self.settings_company_name_input.setPlaceholderText("Razao social")

        self.settings_trade_name_input = QLineEdit()
        self.settings_trade_name_input.setPlaceholderText("Nome fantasia")

        self.settings_document_input = QLineEdit()
        self.settings_document_input.setPlaceholderText("Documento")

        self.settings_email_input = QLineEdit()
        self.settings_email_input.setPlaceholderText("Email")

        self.settings_phone_input = QLineEdit()
        self.settings_phone_input.setPlaceholderText("Telefone")

        self.settings_brand_name_input = QLineEdit()
        self.settings_brand_name_input.setPlaceholderText("Nome exibido no sistema")

        self.settings_brand_subtitle_input = QLineEdit()
        self.settings_brand_subtitle_input.setPlaceholderText("Subtitulo da empresa")

        self.settings_color_palette_combo = QComboBox()
        self._populate_color_palette_combo(self.settings_color_palette_combo)

        self.settings_theme_combo = QComboBox()
        self.settings_theme_combo.addItem("Claro", "light")
        self.settings_theme_combo.addItem("Escuro", "dark")

        self.settings_language_combo = QComboBox()
        self.settings_language_combo.addItem("Portugues brasileiro", "pt-BR")
        self.settings_language_combo.addItem("English (US)", "en-US")

        self.settings_ui_scale_label = QLabel("100%")
        self.settings_ui_scale_label.setObjectName("mutedText")
        self.settings_ui_scale_slider = QSlider(Qt.Orientation.Horizontal)
        self.settings_ui_scale_slider.setMinimum(82)
        self.settings_ui_scale_slider.setMaximum(118)
        self.settings_ui_scale_slider.setValue(100)
        self.settings_ui_scale_slider.valueChanged.connect(self._handle_ui_scale_slider_changed)

        self.settings_backup_enabled_checkbox = QCheckBox("Backup automatico ativo")
        self.settings_backup_enabled_checkbox.setChecked(True)

        self.settings_backup_interval_input = QLineEdit()
        self.settings_backup_interval_input.setPlaceholderText("Intervalo em horas")

        self.settings_backup_path_input = QLineEdit()
        self.settings_backup_path_input.setPlaceholderText("Pasta de backup")

        self.settings_backup_last_run_label = QLabel("Ultimo backup: nunca")
        self.settings_backup_last_run_label.setObjectName("mutedText")

        company_layout = QFormLayout()
        company_layout.setSpacing(10)
        company_layout.addRow("Empresa", self.settings_company_name_input)
        company_layout.addRow("Nome fantasia", self.settings_trade_name_input)
        company_layout.addRow("Documento", self.settings_document_input)
        company_layout.addRow("Email", self.settings_email_input)
        company_layout.addRow("Telefone", self.settings_phone_input)

        company_panel = QFrame()
        company_panel.setObjectName("formSubPanel")
        company_panel_layout = QVBoxLayout(company_panel)
        company_panel_layout.setContentsMargins(12, 12, 12, 12)
        company_panel_layout.setSpacing(8)
        company_title = QLabel("DADOS DA EMPRESA")
        company_title.setObjectName("formGroupTitle")
        company_panel_layout.addWidget(company_title)
        company_panel_layout.addLayout(company_layout)

        branding_layout = QFormLayout()
        branding_layout.setSpacing(10)
        branding_layout.addRow("Nome exibido", self.settings_brand_name_input)
        branding_layout.addRow("Subtitulo", self.settings_brand_subtitle_input)
        branding_layout.addRow("Paleta", self.settings_color_palette_combo)

        branding_panel = QFrame()
        branding_panel.setObjectName("formSubPanel")
        branding_panel_layout = QVBoxLayout(branding_panel)
        branding_panel_layout.setContentsMargins(12, 12, 12, 12)
        branding_panel_layout.setSpacing(8)
        branding_title = QLabel("PERSONALIZACAO")
        branding_title.setObjectName("formGroupTitle")
        branding_panel_layout.addWidget(branding_title)
        branding_panel_layout.addLayout(branding_layout)

        interface_layout = QFormLayout()
        interface_layout.setSpacing(10)
        interface_layout.addRow("Tema", self.settings_theme_combo)
        interface_layout.addRow("Idioma", self.settings_language_combo)
        scale_row = QHBoxLayout()
        scale_row.addWidget(self.settings_ui_scale_slider, 1)
        scale_row.addWidget(self.settings_ui_scale_label)
        interface_layout.addRow("Escala da interface", scale_row)

        interface_panel = QFrame()
        interface_panel.setObjectName("formSubPanel")
        interface_panel_layout = QVBoxLayout(interface_panel)
        interface_panel_layout.setContentsMargins(12, 12, 12, 12)
        interface_panel_layout.setSpacing(8)
        interface_title = QLabel("INTERFACE")
        interface_title.setObjectName("formGroupTitle")
        interface_hint = QLabel("Ajustes locais aplicados ao painel e janelas do operador.")
        interface_hint.setObjectName("mutedText")
        interface_hint.setWordWrap(True)
        interface_panel_layout.addWidget(interface_title)
        interface_panel_layout.addWidget(interface_hint)
        interface_panel_layout.addLayout(interface_layout)

        backup_layout = QFormLayout()
        backup_layout.setSpacing(10)
        backup_layout.addRow("", self.settings_backup_enabled_checkbox)
        backup_layout.addRow("Intervalo", self.settings_backup_interval_input)
        backup_layout.addRow("Destino", self.settings_backup_path_input)

        backup_panel = QFrame()
        backup_panel.setObjectName("formSubPanel")
        backup_panel_layout = QVBoxLayout(backup_panel)
        backup_panel_layout.setContentsMargins(12, 12, 12, 12)
        backup_panel_layout.setSpacing(8)
        backup_title = QLabel("BACKUP E RETENCAO")
        backup_title.setObjectName("formGroupTitle")
        backup_hint = QLabel(
            "Mantenha um destino persistente e revise o ultimo backup antes de atualizacoes."
        )
        backup_hint.setObjectName("mutedText")
        backup_hint.setWordWrap(True)
        backup_panel_layout.addWidget(backup_title)
        backup_panel_layout.addWidget(backup_hint)
        backup_panel_layout.addLayout(backup_layout)
        backup_panel_layout.addWidget(self.settings_backup_last_run_label)
        backup_panel_layout.addStretch()

        settings_details_title = QLabel("RESUMO OPERACIONAL")
        settings_details_title.setObjectName("formGroupTitle")
        self.settings_full_summary = create_summary_text()

        self.settings_form_status = QLabel("")
        self.settings_form_status.setObjectName("mutedText")

        self.settings_save_button = QPushButton("Salvar configuracoes")
        self.settings_save_button.clicked.connect(self._request_settings_save)

        self.settings_run_backup_button = QPushButton("Executar backup agora")
        self.settings_run_backup_button.setObjectName("secondaryButton")
        self.settings_run_backup_button.clicked.connect(self.backup_run_requested.emit)

        actions = QHBoxLayout()
        actions.addStretch()
        actions.addWidget(self.settings_run_backup_button)
        actions.addWidget(self.settings_save_button)

        summary_panel = QFrame()
        summary_panel.setObjectName("formSubPanel")
        summary_panel_layout = QVBoxLayout(summary_panel)
        summary_panel_layout.setContentsMargins(12, 12, 12, 12)
        summary_panel_layout.setSpacing(8)
        summary_panel_layout.addWidget(settings_details_title)
        summary_panel_layout.addWidget(self.settings_full_summary)

        self.settings_tabs = QTabWidget()
        self.settings_tabs.setObjectName("settingsTabs")
        self.settings_tabs.addTab(self._wrap_settings_tab(company_panel), "Empresa")
        self.settings_tabs.addTab(self._wrap_settings_tab(branding_panel), "Aparencia")
        self.settings_tabs.addTab(
            self._wrap_settings_tab(interface_panel, backup_panel),
            "Interface e backup",
        )
        self.settings_tabs.addTab(self._wrap_settings_tab(summary_panel), "Resumo")

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        layout.addWidget(title)
        layout.addWidget(self.settings_tabs)
        layout.addWidget(self.settings_form_status)
        layout.addLayout(actions)

        return panel

    @staticmethod
    def _wrap_settings_tab(*widgets: QFrame) -> QFrame:
        tab = QFrame()
        tab.setObjectName("settingsTab")
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        for widget in widgets:
            layout.addWidget(widget)
        layout.addStretch()
        return tab

    def _build_admin_area_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("formPanel")
        title = QLabel("AREA ADMINISTRATIVA")
        title.setObjectName("sectionTitle")
        description = QLabel("Usuarios, setores, solicitacoes de senha e logs de auditoria.")
        description.setObjectName("mutedText")
        description.setWordWrap(True)
        self.admin_area_actions_layout = create_grid(spacing=10, margins=(0, 0, 0, 0))
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)
        layout.addWidget(title)
        layout.addWidget(description)
        layout.addLayout(self.admin_area_actions_layout)
        layout.addStretch()
        return panel

    def render_admin_area(self) -> None:
        self._set_active_module("admin_area")
        self._clear_layout(self.admin_area_actions_layout)
        allowed_modules = [
            module_key
            for module_key in self._allowed_admin_modules()
            if module_key in {"sectors", "users", "password_resets", "audit_logs"}
        ]
        if not allowed_modules:
            label = QLabel("Seu perfil nao possui acesso a area administrativa.")
            label.setObjectName("mutedText")
            self.admin_area_actions_layout.addWidget(label, 0, 0, 1, GRID_COLUMNS)
            return
        for index, module_key in enumerate(allowed_modules):
            button = QPushButton(self.module_labels[module_key])
            button.setObjectName("adminMenuButton")
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.clicked.connect(
                lambda checked=False, key=module_key: self.module_selected.emit(key)
            )
            self.admin_area_actions_layout.addWidget(button, index // 2, (index % 2) * 6, 1, 6)

    def _build_audit_form(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("formPanel")
        title = QLabel("LOGS E AUDITORIA")
        title.setObjectName("sectionTitle")
        self.audit_full_summary = create_summary_text()
        self.audit_form_status = QLabel("")
        self.audit_form_status.setObjectName("mutedText")
        self.audit_delete_button = QPushButton("Excluir log")
        self.audit_delete_button.setObjectName("dangerButton")
        self.audit_delete_button.setEnabled(False)
        self.audit_delete_button.clicked.connect(self._request_audit_delete)
        actions = QHBoxLayout()
        actions.addStretch()
        actions.addWidget(self.audit_delete_button)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        layout.addWidget(title)
        layout.addWidget(self.audit_full_summary)
        layout.addWidget(self.audit_form_status)
        layout.addLayout(actions)
        return panel
