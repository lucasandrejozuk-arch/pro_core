from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from frontend.app.core.grid import add_widget, create_grid
from frontend.app.widgets import create_summary_text


class DashboardCustomerFormMixin:
    def _build_customer_form(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("formPanel")

        title = QLabel("EDITAR REGISTRO - Cliente")
        title.setObjectName("sectionTitle")

        self.customer_name_input = QLineEdit()
        self.customer_name_input.setPlaceholderText("Nome")

        self.customer_email_input = QLineEdit()
        self.customer_email_input.setPlaceholderText("Email")

        self.customer_phone_input = QLineEdit()
        self.customer_phone_input.setPlaceholderText("(11) 99999-9999")
        self.customer_phone_input.setInputMask("(00) 00000-0000;_")

        self.customer_address_input = QLineEdit()
        self.customer_address_input.setPlaceholderText("Endereco")

        self.customer_notes_input = QLineEdit()
        self.customer_notes_input.setPlaceholderText("Observacoes")

        self.customer_active_checkbox = QCheckBox("Cliente ativo")
        self.customer_active_checkbox.setChecked(True)
        self.customer_active_checkbox.toggled.connect(self._refresh_customer_operational_status)

        self.customer_operational_status = QLabel(
            "Novo cliente: preencha nome, email e telefone para liberar o cadastro."
        )
        self.customer_operational_status.setObjectName("statusBanner")
        self.customer_operational_status.setProperty("level", "warning")
        self.customer_operational_status.setWordWrap(True)

        identity_title = QLabel("DADOS DO CLIENTE")
        identity_title.setObjectName("formGroupTitle")
        identity_form_layout = QFormLayout()
        identity_form_layout.setSpacing(10)
        identity_form_layout.addRow("Nome", self.customer_name_input)
        identity_form_layout.addRow("Email", self.customer_email_input)
        identity_form_layout.addRow("Telefone", self.customer_phone_input)
        identity_form_layout.addRow("", self.customer_active_checkbox)

        identity_panel = QFrame()
        identity_panel.setObjectName("formSubPanel")
        identity_layout = QVBoxLayout(identity_panel)
        identity_layout.setContentsMargins(12, 12, 12, 12)
        identity_layout.setSpacing(8)
        identity_layout.addWidget(identity_title)
        identity_layout.addLayout(identity_form_layout)

        contact_title = QLabel("ENDERECO E OBSERVACOES")
        contact_title.setObjectName("formGroupTitle")
        contact_form_layout = QFormLayout()
        contact_form_layout.setSpacing(10)
        contact_form_layout.addRow("Endereco", self.customer_address_input)
        contact_form_layout.addRow("Observacoes", self.customer_notes_input)

        contact_panel = QFrame()
        contact_panel.setObjectName("formSubPanel")
        contact_layout = QVBoxLayout(contact_panel)
        contact_layout.setContentsMargins(12, 12, 12, 12)
        contact_layout.setSpacing(8)
        contact_layout.addWidget(contact_title)
        contact_layout.addLayout(contact_form_layout)

        fields_layout = create_grid(spacing=8)
        add_widget(fields_layout, identity_panel, 0, 0, 6)
        add_widget(fields_layout, contact_panel, 0, 6, 6)

        self.customer_form_status = QLabel("")
        self.customer_form_status.setObjectName("mutedText")

        self.customer_new_button = QPushButton("Novo")
        self.customer_new_button.setObjectName("secondaryButton")
        self.customer_new_button.clicked.connect(self.clear_customer_form)

        self.customer_delete_button = QPushButton("Excluir")
        self.customer_delete_button.setObjectName("dangerButton")
        self.customer_delete_button.setEnabled(False)
        self.customer_delete_button.clicked.connect(self._request_customer_delete)

        self.customer_save_button = QPushButton("Salvar cliente")
        self.customer_save_button.clicked.connect(self._request_customer_save)

        self.customer_document_path_input = QLineEdit()
        self.customer_document_path_input.setPlaceholderText("Anexo do cliente")
        self.customer_document_path_input.setReadOnly(True)

        self.customer_document_status = QLabel(
            "Anexos: salve ou selecione um cliente antes de enviar evidencias."
        )
        self.customer_document_status.setObjectName("statusBanner")
        self.customer_document_status.setProperty("level", "warning")
        self.customer_document_status.setWordWrap(True)

        self.customer_select_document_button = QPushButton("Selecionar anexo")
        self.customer_select_document_button.setObjectName("secondaryButton")
        self.customer_select_document_button.clicked.connect(self._select_customer_document)

        self.customer_upload_document_button = QPushButton("Enviar anexo")
        self.customer_upload_document_button.clicked.connect(self._request_customer_document_upload)

        details_title = QLabel("DADOS COMPLETOS")
        details_title.setObjectName("formGroupTitle")

        self.customer_full_summary = create_summary_text()

        actions = QHBoxLayout()
        actions.addStretch()
        actions.addWidget(self.customer_new_button)
        actions.addWidget(self.customer_delete_button)
        actions.addWidget(self.customer_save_button)

        document_actions = QHBoxLayout()
        document_actions.addWidget(self.customer_document_path_input, 1)
        document_actions.addWidget(self.customer_select_document_button)
        document_actions.addWidget(self.customer_upload_document_button)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        layout.addWidget(title)
        layout.addWidget(self.customer_operational_status)
        layout.addLayout(fields_layout)
        layout.addWidget(details_title)
        layout.addWidget(self.customer_full_summary)
        layout.addWidget(self.customer_document_status)
        layout.addLayout(document_actions)
        layout.addWidget(self.customer_form_status)
        layout.addLayout(actions)

        return panel
