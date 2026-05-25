from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QVBoxLayout

from frontend.app.widgets import create_summary_text


class DashboardAuditMixin:
    def _build_audit_form(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("formPanel")
        title = QLabel("LOGS E AUDITORIA")
        title.setObjectName("sectionTitle")
        self.audit_full_summary = create_summary_text()
        self.audit_operational_status = QLabel(
            "Status: carregue logs para revisar rastreabilidade operacional."
        )
        self.audit_operational_status.setObjectName("statusBanner")
        self.audit_operational_status.setProperty("level", "warning")
        self.audit_operational_status.setWordWrap(True)
        self.audit_retention_status = QLabel(
            "Retencao: selecione um evento antes de avaliar exclusao."
        )
        self.audit_retention_status.setObjectName("moduleActionHint")
        self.audit_retention_status.setWordWrap(True)
        self.audit_form_status = QLabel("")
        self.audit_form_status.setObjectName("mutedText")
        summary_panel = QFrame()
        summary_panel.setObjectName("formSubPanel")
        summary_panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        summary_layout = QVBoxLayout(summary_panel)
        summary_layout.setContentsMargins(12, 12, 12, 12)
        summary_layout.setSpacing(8)
        summary_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        summary_title = QLabel("DADOS COMPLETOS")
        summary_title.setObjectName("formGroupTitle")
        summary_layout.addWidget(summary_title)
        summary_layout.addWidget(self.audit_full_summary)
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
        layout.addWidget(self.audit_operational_status)
        layout.addWidget(self.audit_retention_status)
        layout.addWidget(summary_panel)
        layout.addWidget(self.audit_form_status)
        layout.addLayout(actions)
        return panel
