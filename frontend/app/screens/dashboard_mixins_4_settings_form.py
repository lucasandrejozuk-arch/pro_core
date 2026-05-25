from __future__ import annotations

import base64
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QSlider,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
)


class DashboardSettingsFormMixin:
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
        self.settings_login_cover_image_data_url = ""
        self.settings_login_cover_preset_combo = QComboBox()
        self.settings_login_cover_preset_combo.addItem("Original do sistema", "original")
        self.settings_login_cover_preset_combo.addItem("Circuito tecnico", "circuit_board")
        self.settings_login_cover_preset_combo.addItem("Bancada premium", "service_bench")
        self.settings_login_cover_preset_combo.addItem("Grade de precisao", "precision_grid")
        self.settings_login_cover_preset_combo.addItem("Imagem anexada", "custom")
        self.settings_login_cover_preset_combo.currentIndexChanged.connect(
            self._handle_login_cover_preset_changed
        )
        self.settings_login_cover_status_label = QLabel(
            "Capa original quando o backend estiver offline."
        )
        self.settings_login_cover_status_label.setObjectName("mutedText")
        self.settings_login_cover_status_label.setWordWrap(True)
        self.settings_login_cover_select_button = QPushButton("Selecionar imagem PNG/JPEG")
        self.settings_login_cover_select_button.setObjectName("secondaryButton")
        self.settings_login_cover_select_button.clicked.connect(self._select_login_cover_image)
        self.settings_login_cover_clear_button = QPushButton("Remover anexo")
        self.settings_login_cover_clear_button.setObjectName("secondaryButton")
        self.settings_login_cover_clear_button.clicked.connect(self._clear_login_cover_image)
        self.settings_theme_combo = QComboBox()
        self.settings_theme_combo.addItem("Claro", "light")
        self.settings_theme_combo.addItem("Escuro", "dark")
        self.settings_language_combo = QComboBox()
        self.settings_language_combo.addItem("Portugues brasileiro", "pt-BR")
        self.settings_language_combo.addItem("English (United States)", "en-US")
        default_language_index = self.settings_language_combo.findData("en-US")
        if default_language_index >= 0:
            self.settings_language_combo.setCurrentIndex(default_language_index)
        self.settings_ui_scale_label = QLabel("100%")
        self.settings_ui_scale_label.setObjectName("mutedText")
        self.settings_ui_scale_slider = QSlider(Qt.Orientation.Horizontal)
        self.settings_ui_scale_slider.setMinimum(82)
        self.settings_ui_scale_slider.setMaximum(118)
        self.settings_ui_scale_slider.setValue(100)
        self.settings_ui_scale_slider.valueChanged.connect(self._handle_ui_scale_slider_changed)
        self.settings_ui_scale_slider.setMaximum(150)
        self.settings_ui_scale_slider.setTickInterval(4)
        self.settings_ui_scale_slider.setPageStep(4)
        self.settings_ui_scale_slider.setSingleStep(2)
        self.settings_ui_scale_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.settings_backup_enabled_checkbox = QCheckBox("Backup automatico ativo")
        self.settings_backup_enabled_checkbox.setChecked(True)
        self.settings_backup_interval_input = QSpinBox()
        self.settings_backup_interval_input.setMinimum(1)
        self.settings_backup_interval_input.setMaximum(720)
        self.settings_backup_interval_input.setValue(24)
        self.settings_backup_interval_input.setAccelerated(True)
        self.settings_backup_interval_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.settings_backup_interval_input.setMinimumWidth(96)
        self.settings_backup_interval_input.setMaximumWidth(120)
        self.settings_backup_interval_unit_combo = QComboBox()
        self.settings_backup_interval_unit_combo.addItem("Horas", "hours")
        self.settings_backup_interval_unit_combo.addItem("Dias", "days")
        self.settings_backup_interval_unit_combo.addItem("Semanas", "weeks")
        self.settings_backup_interval_unit_combo.currentIndexChanged.connect(
            self._handle_backup_interval_unit_changed
        )
        self.settings_backup_destination_mode_combo = QComboBox()
        self.settings_backup_destination_mode_combo.addItem(
            "Pasta interna do Pro Core",
            "internal",
        )
        self.settings_backup_destination_mode_combo.addItem(
            "Local personalizado",
            "custom",
        )
        self.settings_backup_destination_mode_combo.currentIndexChanged.connect(
            self._handle_backup_destination_mode_changed
        )
        self.settings_backup_path_input = QLineEdit()
        self.settings_backup_path_input.setPlaceholderText("Pasta de backup")
        self.settings_backup_browse_button = QPushButton("Selecionar pasta")
        self.settings_backup_browse_button.setObjectName("secondaryButton")
        self.settings_backup_browse_button.clicked.connect(self._select_backup_directory)
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
        company_panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
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
        branding_layout.addRow("Tema", self.settings_theme_combo)
        branding_layout.addRow("Capa do login", self.settings_login_cover_preset_combo)
        cover_actions = QHBoxLayout()
        cover_actions.addWidget(self.settings_login_cover_select_button)
        cover_actions.addWidget(self.settings_login_cover_clear_button)
        branding_layout.addRow("Imagem", cover_actions)
        branding_layout.addRow("", self.settings_login_cover_status_label)
        branding_panel = QFrame()
        branding_panel.setObjectName("formSubPanel")
        branding_panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        branding_panel_layout = QVBoxLayout(branding_panel)
        branding_panel_layout.setContentsMargins(12, 12, 12, 12)
        branding_panel_layout.setSpacing(8)
        branding_title = QLabel("APARENCIA")
        branding_title.setObjectName("formGroupTitle")
        branding_panel_layout.addWidget(branding_title)
        branding_panel_layout.addLayout(branding_layout)
        interface_layout = QFormLayout()
        interface_layout.setSpacing(10)
        interface_layout.addRow("Idioma", self.settings_language_combo)
        scale_row = QHBoxLayout()
        scale_row.addWidget(self.settings_ui_scale_slider, 1)
        scale_row.addWidget(self.settings_ui_scale_label)
        interface_layout.addRow("Escala da interface", scale_row)
        interface_panel = QFrame()
        interface_panel.setObjectName("formSubPanel")
        interface_panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        interface_panel_layout = QVBoxLayout(interface_panel)
        interface_panel_layout.setContentsMargins(12, 12, 12, 12)
        interface_panel_layout.setSpacing(8)
        interface_title = QLabel("INTERFACE")
        interface_title.setObjectName("formGroupTitle")
        interface_hint = QLabel(
            "Idioma e escala local da interface. A troca de idioma aplica os textos "
            "dinamicos e mensagens operacionais do sistema."
        )
        interface_hint.setObjectName("mutedText")
        interface_hint.setWordWrap(True)
        interface_panel_layout.addWidget(interface_title)
        interface_panel_layout.addWidget(interface_hint)
        interface_panel_layout.addLayout(interface_layout)
        backup_layout = QFormLayout()
        backup_layout.setSpacing(10)
        interval_row = QHBoxLayout()
        interval_row.setSpacing(8)
        interval_row.addWidget(self.settings_backup_interval_input)
        interval_row.addWidget(self.settings_backup_interval_unit_combo, 0)
        interval_row.addStretch(1)
        path_row = QHBoxLayout()
        path_row.setSpacing(8)
        path_row.addWidget(self.settings_backup_path_input, 1)
        path_row.addWidget(self.settings_backup_browse_button)
        backup_layout.addRow("", self.settings_backup_enabled_checkbox)
        backup_layout.addRow("Frequencia", interval_row)
        backup_layout.addRow("Destino", self.settings_backup_destination_mode_combo)
        backup_layout.addRow("Caminho", path_row)
        backup_panel = QFrame()
        backup_panel.setObjectName("formSubPanel")
        backup_panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        backup_panel_layout = QVBoxLayout(backup_panel)
        backup_panel_layout.setContentsMargins(12, 12, 12, 12)
        backup_panel_layout.setSpacing(8)
        backup_title = QLabel("BACKUP E RETENCAO")
        backup_title.setObjectName("formGroupTitle")
        backup_hint = QLabel(
            "Defina a frequencia, a escala de tempo e onde os arquivos serao gravados."
        )
        backup_hint.setObjectName("mutedText")
        backup_hint.setWordWrap(True)
        backup_panel_layout.addWidget(backup_title)
        backup_panel_layout.addWidget(backup_hint)
        backup_panel_layout.addLayout(backup_layout)
        backup_panel_layout.addWidget(self.settings_backup_last_run_label)
        self.settings_operational_status = QLabel(
            "Status: carregue configuracoes para revisar identidade e interface."
        )
        self.settings_operational_status.setObjectName("statusBanner")
        self.settings_operational_status.setProperty("level", "warning")
        self.settings_operational_status.setWordWrap(True)
        self.settings_backup_status = QLabel("Backup: informe intervalo e destino antes de salvar.")
        self.settings_backup_status.setObjectName("moduleActionHint")
        self.settings_backup_status.setWordWrap(True)
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
        self.settings_tabs = QTabWidget()
        self.settings_tabs.setObjectName("settingsTabs")
        self._settings_context_ready = False
        self.settings_tabs.addTab(self._wrap_settings_tab(company_panel), "Empresa")
        self.settings_tabs.addTab(self._wrap_settings_tab(branding_panel), "Aparencia")
        self.settings_tabs.addTab(
            self._wrap_settings_tab(interface_panel),
            "Interface",
        )
        self.settings_tabs.addTab(self._wrap_settings_tab(backup_panel), "Backup")
        self.settings_tabs.currentChanged.connect(self._handle_settings_context_changed)
        for widget in (
            self.settings_company_name_input,
            self.settings_trade_name_input,
            self.settings_document_input,
            self.settings_email_input,
            self.settings_phone_input,
            self.settings_brand_name_input,
            self.settings_brand_subtitle_input,
            self.settings_backup_path_input,
        ):
            widget.textChanged.connect(self._handle_settings_context_changed)
        for widget in (
            self.settings_color_palette_combo,
            self.settings_login_cover_preset_combo,
            self.settings_theme_combo,
            self.settings_language_combo,
            self.settings_backup_interval_unit_combo,
            self.settings_backup_destination_mode_combo,
        ):
            widget.currentIndexChanged.connect(self._handle_settings_context_changed)
        self.settings_backup_enabled_checkbox.toggled.connect(self._handle_settings_context_changed)
        self.settings_backup_interval_input.valueChanged.connect(
            self._handle_settings_context_changed
        )
        for form_layout in (company_layout, branding_layout, interface_layout, backup_layout):
            form_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
            form_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows)
            form_layout.setFormAlignment(Qt.AlignmentFlag.AlignTop)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        layout.addWidget(title)
        layout.addWidget(self.settings_operational_status)
        layout.addWidget(self.settings_backup_status)
        layout.addWidget(self.settings_tabs, 1)
        layout.addWidget(self.settings_form_status)
        layout.addLayout(actions)
        self._handle_login_cover_preset_changed()
        self._handle_backup_interval_unit_changed()
        self._handle_backup_destination_mode_changed()
        if hasattr(self, "_restore_settings_resume_tab"):
            self._restore_settings_resume_tab()
        if hasattr(self, "_capture_settings_form_snapshot"):
            self.settings_form_snapshot = self._capture_settings_form_snapshot()
        self._settings_context_ready = True
        return panel

    @staticmethod
    def _wrap_settings_tab(*widgets: QFrame) -> QFrame:
        tab = QFrame()
        tab.setObjectName("settingsTab")
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        for widget in widgets:
            widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
            layout.addWidget(widget)
        layout.addStretch(1)
        return tab

    def _handle_login_cover_preset_changed(self) -> None:
        preset = str(self.settings_login_cover_preset_combo.currentData() or "original")
        is_custom = preset == "custom"
        self.settings_login_cover_select_button.setEnabled(is_custom)
        self.settings_login_cover_clear_button.setEnabled(is_custom)
        if is_custom:
            if self.settings_login_cover_image_data_url:
                self.settings_login_cover_status_label.setText(
                    "Imagem anexada pronta para a tela de login conectada ao backend."
                )
            else:
                self.settings_login_cover_status_label.setText(
                    "Selecione um PNG ou JPEG de ate 2 MB para usar como capa conectada."
                )
            return
        self.settings_login_cover_status_label.setText(
            "Capa original sera usada quando o backend estiver offline."
        )

    def _handle_backup_destination_mode_changed(self) -> None:
        mode = str(self.settings_backup_destination_mode_combo.currentData() or "internal")
        is_custom = mode == "custom"
        self.settings_backup_path_input.setReadOnly(not is_custom)
        self.settings_backup_browse_button.setEnabled(is_custom)
        if is_custom:
            self.settings_backup_path_input.setPlaceholderText("Selecione uma pasta personalizada")
            return
        self.settings_backup_path_input.setPlaceholderText("Pasta interna do Pro Core")
        self.settings_backup_path_input.setText("backups")

    def _handle_backup_interval_unit_changed(self) -> None:
        unit_key = str(self.settings_backup_interval_unit_combo.currentData() or "hours")
        maximum_by_unit = {
            "hours": 720,
            "days": 30,
            "weeks": 4,
        }
        self.settings_backup_interval_input.setMaximum(maximum_by_unit.get(unit_key, 720))

    def _select_backup_directory(self) -> None:
        directory = QFileDialog.getExistingDirectory(
            self,
            "Selecionar pasta de backup",
            self.settings_backup_path_input.text().strip() or "",
        )
        if directory:
            self.settings_backup_path_input.setText(directory)

    def _select_login_cover_image(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar capa do login",
            "",
            "Imagens (*.png *.jpg *.jpeg)",
        )
        if not path:
            return
        image_path = Path(path)
        suffix = image_path.suffix.lower()
        if suffix not in {".png", ".jpg", ".jpeg"}:
            self.set_settings_form_status("Selecione um arquivo PNG ou JPEG.", is_error=True)
            return
        try:
            image_bytes = image_path.read_bytes()
        except OSError as exc:
            self.set_settings_form_status(f"Falha ao ler imagem: {exc}", is_error=True)
            return
        if not image_bytes:
            self.set_settings_form_status("A imagem selecionada esta vazia.", is_error=True)
            return
        if len(image_bytes) > 2 * 1024 * 1024:
            self.set_settings_form_status("A imagem deve ter no maximo 2 MB.", is_error=True)
            return
        mime_type = "image/png" if suffix == ".png" else "image/jpeg"
        encoded = base64.b64encode(image_bytes).decode("ascii")
        self.settings_login_cover_image_data_url = f"data:{mime_type};base64,{encoded}"
        self._select_combo_value(self.settings_login_cover_preset_combo, "custom")
        self.settings_login_cover_status_label.setText(
            f"Imagem anexada: {image_path.name} ({len(image_bytes) // 1024 or 1} KB)."
        )
        self.set_settings_form_status("Imagem da capa preparada para salvar.")

    def _clear_login_cover_image(self) -> None:
        self.settings_login_cover_image_data_url = ""
        self.settings_login_cover_status_label.setText("Anexo removido. Selecione outra imagem.")
