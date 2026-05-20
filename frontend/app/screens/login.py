from __future__ import annotations

from PySide6.QtCore import QPointF, QSettings, Qt, Signal
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPainterPath, QPen
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

from frontend.app.core.display import detect_display_profile
from frontend.app.core.grid import add_widget, create_grid


class LoginBrandPanel(QFrame):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("brandPanel")

    def paintEvent(self, event) -> None:  # type: ignore[override]
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect()
        background = QLinearGradient(rect.topLeft(), rect.bottomRight())
        background.setColorAt(0.0, QColor("#063b63"))
        background.setColorAt(0.55, QColor("#0a5a86"))
        background.setColorAt(1.0, QColor("#042338"))
        painter.fillRect(rect, background)

        painter.setPen(Qt.PenStyle.NoPen)
        for index, color in enumerate(("#ffffff", "#7dd3fc", "#0ea5e9", "#dbeafe")):
            alpha = 20 - (index * 3)
            glow = QColor(color)
            glow.setAlpha(alpha)
            painter.setBrush(glow)
            painter.drawEllipse(
                QPointF(rect.width() * (0.18 + index * 0.18), rect.height() * 0.18),
                rect.width() * (0.20 - index * 0.025),
                rect.height() * (0.16 - index * 0.018),
            )

        horizon = rect.height() * 0.55
        painter.setPen(QPen(QColor(255, 255, 255, 34), 1.2))
        for offset in range(-4, 7):
            y = horizon + offset * 28
            painter.drawLine(0, int(y), rect.width(), int(y + offset * 10))

        painter.setPen(Qt.PenStyle.NoPen)
        for column in range(9):
            x = rect.width() * (0.08 + column * 0.105)
            width = rect.width() * (0.045 + (column % 3) * 0.01)
            height = rect.height() * (0.22 + (column % 4) * 0.05)
            top = horizon - height
            panel_color = QColor(2, 18, 34, 98)
            painter.setBrush(panel_color)
            painter.drawRoundedRect(int(x), int(top), int(width), int(height), 7, 7)
            painter.setBrush(QColor(125, 211, 252, 32))
            painter.drawRoundedRect(int(x + 7), int(top + 12), int(width - 14), 5, 2, 2)

        bench_path = QPainterPath()
        bench_path.moveTo(rect.width() * 0.06, rect.height() * 0.66)
        bench_path.lineTo(rect.width() * 0.96, rect.height() * 0.58)
        bench_path.lineTo(rect.width(), rect.height())
        bench_path.lineTo(0, rect.height())
        bench_path.closeSubpath()
        painter.setBrush(QColor(1, 12, 23, 150))
        painter.drawPath(bench_path)

        painter.setPen(QPen(QColor(125, 211, 252, 54), 2))
        for line in range(7):
            x = rect.width() * (0.12 + line * 0.11)
            painter.drawLine(
                int(x),
                int(rect.height() * 0.70),
                int(x + rect.width() * 0.18),
                int(rect.height() * 0.96),
            )

        painter.fillRect(rect, QColor(1, 13, 24, 86))


class LoginWindow(QWidget):
    login_requested = Signal(str, str)
    password_reset_requested = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        profile = detect_display_profile()
        self.setWindowTitle("PRO CORE")
        self.setMinimumSize(round(980 * profile.ui_scale), round(620 * profile.ui_scale))
        self.setObjectName("loginWindow")

        self.brand_label = QLabel("PRO CORE")
        self.brand_label.setObjectName("brandTitle")

        self.tagline_label = QLabel("Gestao completa para assistencias tecnicas")
        self.tagline_label.setObjectName("brandSubtitle")
        self.tagline_label.setWordWrap(True)

        brand_panel = LoginBrandPanel()
        brand_layout = QVBoxLayout(brand_panel)
        brand_margin = round(22 * profile.ui_scale)
        brand_layout.setContentsMargins(brand_margin, brand_margin, brand_margin, brand_margin)
        brand_layout.addStretch()
        brand_layout.addWidget(self.brand_label)
        brand_layout.addWidget(self.tagline_label)
        brand_layout.addStretch()

        heading = QLabel("Entrar")
        heading.setObjectName("formTitle")

        helper = QLabel("Use sua conta PRO CORE para acessar os modulos operacionais.")
        helper.setObjectName("mutedText")
        helper.setWordWrap(True)

        self.backend_status_label = QLabel("Verificando conexao com o backend...")
        self.backend_status_label.setObjectName("statusBanner")
        self.backend_status_label.setProperty("level", "warning")
        self.backend_status_label.setWordWrap(True)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Senha")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.returnPressed.connect(self._request_login)

        self.password_visibility_button = QPushButton("Exibir senha")
        self.password_visibility_button.setObjectName("secondaryButton")
        self.password_visibility_button.setCheckable(True)
        self.password_visibility_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.password_visibility_button.setFixedWidth(round(118 * profile.ui_scale))
        self.password_visibility_button.toggled.connect(self._toggle_password_visibility)

        password_row = QWidget()
        password_layout = QHBoxLayout(password_row)
        password_layout.setContentsMargins(0, 0, 0, 0)
        password_layout.setSpacing(round(8 * profile.ui_scale))
        password_layout.addWidget(self.password_input, 1)
        password_layout.addWidget(self.password_visibility_button)

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
        form_margin = round(24 * profile.ui_scale)
        form_layout.setContentsMargins(form_margin, form_margin, form_margin, form_margin)
        form_layout.setSpacing(round(8 * profile.ui_scale))
        form_layout.addStretch()
        form_layout.addWidget(heading)
        form_layout.addWidget(helper)
        form_layout.addWidget(self.backend_status_label)
        form_layout.addWidget(self.email_input)
        form_layout.addWidget(password_row)
        form_layout.addWidget(self.remember_user_checkbox)
        form_layout.addWidget(self.error_label)
        form_layout.addWidget(self.submit_button)
        form_layout.addWidget(self.forgot_password_button)
        form_layout.addStretch()

        layout = create_grid()
        self.setLayout(layout)
        add_widget(layout, brand_panel, 0, 0, 7)
        add_widget(layout, form_panel, 0, 7, 5)
        layout.setRowStretch(0, 1)
        self._load_remembered_user()

    def set_loading(self, is_loading: bool) -> None:
        self.submit_button.setEnabled(not is_loading)
        self.forgot_password_button.setEnabled(not is_loading)
        self.password_visibility_button.setEnabled(not is_loading)
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

    def apply_branding(self, settings: dict) -> None:
        brand_name = str(settings.get("brand_name") or "PRO CORE")
        brand_subtitle = str(
            settings.get("brand_subtitle") or "Gestao completa para assistencias tecnicas"
        )
        self.brand_label.setText(brand_name)
        self.tagline_label.setText(brand_subtitle)
        self.setWindowTitle(brand_name)

    def set_backend_connection_status(self, is_connected: bool, message: str | None = None) -> None:
        self.backend_status_label.setProperty("level", "" if is_connected else "error")
        self.backend_status_label.setText(
            message or ("Backend conectado." if is_connected else "Backend indisponivel.")
        )
        self.backend_status_label.style().unpolish(self.backend_status_label)
        self.backend_status_label.style().polish(self.backend_status_label)

    def clear_form(self) -> None:
        self.password_input.clear()
        self.error_label.clear()
        self.set_loading(False)
        self.set_password_reset_loading(False)
        self.password_visibility_button.setChecked(False)

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

    def _toggle_password_visibility(self, checked: bool) -> None:
        self.password_input.setEchoMode(
            QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password
        )
        self.password_visibility_button.setText("Ocultar senha" if checked else "Exibir senha")

    def _load_remembered_user(self) -> None:
        settings = QSettings("PRO CORE", "PRO CORE")
        remembered_email = str(settings.value("login/remembered_email", "") or "")
        if not remembered_email:
            return

        self.email_input.setText(remembered_email)
        self.remember_user_checkbox.setChecked(True)
