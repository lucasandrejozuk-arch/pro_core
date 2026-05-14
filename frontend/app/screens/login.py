from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtCore import QSettings
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class LoginWindow(QWidget):
    login_requested = Signal(str, str)
    password_reset_requested = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("PRO CORE")
        self.setMinimumSize(980, 620)
        self.setObjectName("loginWindow")

        brand = QLabel("PRO CORE")
        brand.setObjectName("brandTitle")

        tagline = QLabel("Gestao completa para assistencias tecnicas")
        tagline.setObjectName("brandSubtitle")
        tagline.setWordWrap(True)

        brand_panel = QFrame()
        brand_panel.setObjectName("brandPanel")
        brand_layout = QVBoxLayout(brand_panel)
        brand_layout.setContentsMargins(44, 44, 44, 44)
        brand_layout.addStretch()
        brand_layout.addWidget(brand)
        brand_layout.addWidget(tagline)
        brand_layout.addStretch()

        heading = QLabel("Entrar")
        heading.setObjectName("formTitle")

        helper = QLabel("Use sua conta PRO CORE para acessar os modulos operacionais.")
        helper.setObjectName("mutedText")
        helper.setWordWrap(True)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Senha")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.returnPressed.connect(self._request_login)

        self.remember_user_checkbox = QCheckBox("Lembrar usuario")

        self.error_label = QLabel("")
        self.error_label.setObjectName("errorText")
        self.error_label.setWordWrap(True)

        self.submit_button = QPushButton("Entrar")
        self.submit_button.clicked.connect(self._request_login)

        self.forgot_password_button = QPushButton("Esqueci minha senha")
        self.forgot_password_button.setObjectName("secondaryButton")
        self.forgot_password_button.clicked.connect(self._request_password_reset)

        form_panel = QFrame()
        form_panel.setObjectName("formPanel")
        form_layout = QVBoxLayout(form_panel)
        form_layout.setContentsMargins(64, 64, 64, 64)
        form_layout.setSpacing(16)
        form_layout.addStretch()
        form_layout.addWidget(heading)
        form_layout.addWidget(helper)
        form_layout.addWidget(self.email_input)
        form_layout.addWidget(self.password_input)
        form_layout.addWidget(self.remember_user_checkbox)
        form_layout.addWidget(self.error_label)
        form_layout.addWidget(self.submit_button)
        form_layout.addWidget(self.forgot_password_button)
        form_layout.addStretch()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(brand_panel, 5)
        layout.addWidget(form_panel, 4)
        self._load_remembered_user()

    def set_loading(self, is_loading: bool) -> None:
        self.submit_button.setEnabled(not is_loading)
        self.forgot_password_button.setEnabled(not is_loading)
        self.submit_button.setText("Entrando..." if is_loading else "Entrar")

    def set_password_reset_loading(self, is_loading: bool) -> None:
        self.forgot_password_button.setEnabled(not is_loading)
        self.submit_button.setEnabled(not is_loading)
        self.forgot_password_button.setText("Enviando..." if is_loading else "Esqueci minha senha")

    def set_error(self, message: str) -> None:
        self.error_label.setObjectName("errorText")
        self.error_label.setText(message)
        self.error_label.style().unpolish(self.error_label)
        self.error_label.style().polish(self.error_label)

    def set_info(self, message: str) -> None:
        self.error_label.setObjectName("mutedText")
        self.error_label.setText(message)
        self.error_label.style().unpolish(self.error_label)
        self.error_label.style().polish(self.error_label)

    def clear_form(self) -> None:
        self.password_input.clear()
        self.error_label.clear()
        self.set_loading(False)
        self.set_password_reset_loading(False)

    def persist_remembered_user(self, email: str) -> None:
        settings = QSettings("PRO CORE", "PRO CORE")
        if self.remember_user_checkbox.isChecked():
            settings.setValue("login/remembered_email", email)
            return

        settings.remove("login/remembered_email")

    def _request_login(self) -> None:
        email = self.email_input.text().strip()
        password = self.password_input.text()

        if not email or not password:
            self.set_error("Informe email e senha.")
            return

        self.set_error("")
        self.login_requested.emit(email, password)

    def _request_password_reset(self) -> None:
        email = self.email_input.text().strip()
        if not email:
            self.set_error("Informe o email da conta.")
            return

        self.set_error("")
        self.password_reset_requested.emit(email)

    def _load_remembered_user(self) -> None:
        settings = QSettings("PRO CORE", "PRO CORE")
        remembered_email = str(settings.value("login/remembered_email", "") or "")
        if not remembered_email:
            return

        self.email_input.setText(remembered_email)
        self.remember_user_checkbox.setChecked(True)
