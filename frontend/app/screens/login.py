from __future__ import annotations

import base64
import binascii

from PySide6.QtCore import QPointF, QSettings, Qt, Signal
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPainterPath, QPen, QPixmap
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
from frontend.app.core.i18n import normalize_language, translate_ui_text


class LoginBrandPanel(QFrame):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("brandPanel")
        self._cover_preset = "original"
        self._cover_pixmap: QPixmap | None = None

    def apply_cover(self, settings: dict, *, backend_connected: bool) -> None:
        if not backend_connected:
            self._cover_preset = "original"
            self._cover_pixmap = None
            self.update()
            return

        preset = str(settings.get("login_cover_preset") or "original")
        self._cover_preset = (
            preset
            if preset in {"original", "circuit_board", "service_bench", "precision_grid", "custom"}
            else "original"
        )
        self._cover_pixmap = self._decode_cover_pixmap(
            str(settings.get("login_cover_image_data_url") or "")
            if self._cover_preset == "custom"
            else ""
        )
        if self._cover_preset == "custom" and self._cover_pixmap is None:
            self._cover_preset = "original"
        self.update()

    def paintEvent(self, event) -> None:  # type: ignore[override]
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect()
        if self._cover_pixmap is not None:
            scaled = self._cover_pixmap.scaled(
                rect.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
            painter.drawPixmap(
                (rect.width() - scaled.width()) // 2,
                (rect.height() - scaled.height()) // 2,
                scaled,
            )
            painter.fillRect(rect, QColor(1, 13, 24, 118))
            self._paint_precision_overlay(painter, rect, QColor(125, 211, 252, 44))
            return

        background = QLinearGradient(rect.topLeft(), rect.bottomRight())
        colors = {
            "original": ("#063b63", "#0a5a86", "#042338"),
            "circuit_board": ("#05352f", "#0f766e", "#05251f"),
            "service_bench": ("#1f2937", "#0f766e", "#111827"),
            "precision_grid": ("#0f172a", "#164e63", "#020617"),
        }.get(self._cover_preset, ("#063b63", "#0a5a86", "#042338"))
        background.setColorAt(0.0, QColor(colors[0]))
        background.setColorAt(0.55, QColor(colors[1]))
        background.setColorAt(1.0, QColor(colors[2]))
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
        if self._cover_preset == "circuit_board":
            self._paint_circuit_overlay(painter, rect)
        else:
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

        if self._cover_preset == "precision_grid":
            self._paint_precision_overlay(painter, rect, QColor(255, 255, 255, 34))

    @staticmethod
    def _decode_cover_pixmap(data_url: str) -> QPixmap | None:
        if not data_url:
            return None
        lowered = data_url.lower()
        prefixes = (
            "data:image/png;base64,",
            "data:image/jpeg;base64,",
            "data:image/jpg;base64,",
        )
        prefix = next((candidate for candidate in prefixes if lowered.startswith(candidate)), None)
        if prefix is None:
            return None
        try:
            decoded = base64.b64decode(data_url[len(prefix) :], validate=True)
        except (binascii.Error, ValueError):
            return None
        pixmap = QPixmap()
        if not pixmap.loadFromData(decoded):
            return None
        return pixmap

    @staticmethod
    def _paint_circuit_overlay(painter: QPainter, rect) -> None:
        painter.setPen(QPen(QColor(125, 211, 252, 64), 2))
        for row in range(6):
            y = int(rect.height() * (0.18 + row * 0.11))
            painter.drawLine(int(rect.width() * 0.10), y, int(rect.width() * 0.88), y)
            for node in range(4):
                x = int(rect.width() * (0.18 + node * 0.18))
                painter.drawEllipse(QPointF(x, y), 4, 4)
                painter.drawLine(x, y, x, int(y + rect.height() * 0.07))

    @staticmethod
    def _paint_precision_overlay(painter: QPainter, rect, color: QColor) -> None:
        painter.setPen(QPen(color, 1))
        step = max(28, rect.width() // 14)
        for x in range(0, rect.width(), step):
            painter.drawLine(x, 0, x, rect.height())
        for y in range(0, rect.height(), step):
            painter.drawLine(0, y, rect.width(), y)


class LoginWindow(QWidget):
    login_requested = Signal(str, str)
    password_reset_requested = Signal(str)
    backend_reconnect_requested = Signal()

    def __init__(self) -> None:
        super().__init__()
        profile = detect_display_profile()
        self.setWindowTitle("PRO CORE")
        self.setMinimumSize(round(980 * profile.ui_scale), round(620 * profile.ui_scale))
        self.setObjectName("loginWindow")

        self.brand_label = QLabel("PRO CORE")
        self.brand_label.setObjectName("brandTitle")
        self.brand_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.tagline_label = QLabel("Gestao completa para assistencias tecnicas")
        self.tagline_label.setObjectName("brandSubtitle")
        self.tagline_label.setWordWrap(True)
        self.tagline_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.brand_panel = LoginBrandPanel()
        brand_layout = QVBoxLayout(self.brand_panel)
        brand_margin = round(22 * profile.ui_scale)
        brand_layout.setContentsMargins(brand_margin, brand_margin, brand_margin, brand_margin)
        brand_layout.setSpacing(round(10 * profile.ui_scale))
        brand_layout.addStretch(3)
        brand_layout.addWidget(self.brand_label, 0, Qt.AlignmentFlag.AlignHCenter)
        brand_layout.addWidget(self.tagline_label, 0, Qt.AlignmentFlag.AlignHCenter)
        brand_layout.addStretch(9)

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
        self.forgot_password_button.setObjectName("forgotPasswordButton")
        self.forgot_password_button.clicked.connect(self._request_password_reset)

        self.backend_reconnect_button = QPushButton("Conectar/Reiniciar backend")
        self.backend_reconnect_button.setObjectName("secondaryButton")
        self.backend_reconnect_button.clicked.connect(self._request_backend_reconnect)

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
        form_layout.addWidget(self.backend_reconnect_button)
        form_layout.addStretch()

        layout = create_grid()
        self.setLayout(layout)
        add_widget(layout, self.brand_panel, 0, 0, 7)
        add_widget(layout, form_panel, 0, 7, 5)
        layout.setRowStretch(0, 1)
        self._load_remembered_user()

    def set_loading(self, is_loading: bool) -> None:
        self.submit_button.setEnabled(not is_loading)
        self.forgot_password_button.setEnabled(not is_loading)
        self.backend_reconnect_button.setEnabled(not is_loading)
        self.password_visibility_button.setEnabled(not is_loading)
        self.submit_button.setText("Entrando..." if is_loading else "Entrar")

    def set_password_reset_loading(self, is_loading: bool) -> None:
        self.forgot_password_button.setEnabled(not is_loading)
        self.submit_button.setEnabled(not is_loading)
        self.backend_reconnect_button.setEnabled(not is_loading)
        self.forgot_password_button.setText("Enviando..." if is_loading else "Esqueci minha senha")

    def set_backend_reconnect_loading(self, is_loading: bool) -> None:
        self.backend_reconnect_button.setEnabled(not is_loading)
        self.backend_reconnect_button.setText(
            "Conectando/Reiniciando..." if is_loading else "Conectar/Reiniciar backend"
        )

    def set_error(self, message: str) -> None:
        self.error_label.setObjectName("errorText")
        language = normalize_language(
            str(QSettings("PRO CORE", "PRO CORE").value("appearance/language", "pt-BR") or "pt-BR")
        )
        self.error_label.setText(translate_ui_text(message, language))
        self.error_label.style().unpolish(self.error_label)
        self.error_label.style().polish(self.error_label)

    def set_info(self, message: str) -> None:
        self.error_label.setObjectName("mutedText")
        language = normalize_language(
            str(QSettings("PRO CORE", "PRO CORE").value("appearance/language", "pt-BR") or "pt-BR")
        )
        self.error_label.setText(translate_ui_text(message, language))
        self.error_label.style().unpolish(self.error_label)
        self.error_label.style().polish(self.error_label)

    def apply_branding(self, settings: dict, *, backend_connected: bool = True) -> None:
        brand_name = str(settings.get("brand_name") or "PRO CORE")
        brand_subtitle = str(
            settings.get("brand_subtitle") or "Gestao completa para assistencias tecnicas"
        )
        self.brand_label.setText(brand_name)
        self.tagline_label.setText(brand_subtitle)
        self.setWindowTitle(brand_name)
        self.brand_panel.apply_cover(settings, backend_connected=backend_connected)

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

    def _request_backend_reconnect(self) -> None:
        self.set_error("")
        self.backend_reconnect_requested.emit()

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
