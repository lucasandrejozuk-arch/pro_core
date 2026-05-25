from __future__ import annotations

from PySide6.QtCore import QSettings, Signal
from PySide6.QtWidgets import QFrame, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget

from frontend.app.core.display import detect_display_profile
from frontend.app.core.grid import add_widget, create_grid
from frontend.app.core.i18n import normalize_language, translate_ui_text


class PasswordChangeWindow(QWidget):
    password_change_requested = Signal(str, str)

    def __init__(self) -> None:
        super().__init__()
        profile = detect_display_profile()
        self.setWindowTitle("PRO CORE - Alterar senha")
        self.setMinimumSize(round(620 * profile.ui_scale), round(460 * profile.ui_scale))
        self.setObjectName("passwordWindow")

        self.form_panel = QFrame()
        self.form_panel.setObjectName("formPanel")

        title = QLabel("Alterar senha")
        title.setObjectName("formTitle")

        helper = QLabel("Este usuario precisa definir uma senha propria antes de continuar.")
        helper.setObjectName("mutedText")
        helper.setWordWrap(True)

        self.current_password_input = QLineEdit()
        self.current_password_input.setPlaceholderText("Senha atual")
        self.current_password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.new_password_input = QLineEdit()
        self.new_password_input.setPlaceholderText("Nova senha")
        self.new_password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("Confirmar nova senha")
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_input.returnPressed.connect(self._request_change)

        self.error_label = QLabel("")
        self.error_label.setObjectName("errorText")
        self.error_label.setWordWrap(True)

        self.submit_button = QPushButton("Salvar senha")
        self.submit_button.clicked.connect(self._request_change)

        panel_layout = QVBoxLayout(self.form_panel)
        panel_margin = round(44 * profile.ui_scale)
        panel_layout.setContentsMargins(panel_margin, panel_margin, panel_margin, panel_margin)
        panel_layout.setSpacing(round(16 * profile.ui_scale))
        panel_layout.addWidget(title)
        panel_layout.addWidget(helper)
        panel_layout.addWidget(self.current_password_input)
        panel_layout.addWidget(self.new_password_input)
        panel_layout.addWidget(self.confirm_password_input)
        panel_layout.addWidget(self.error_label)
        panel_layout.addWidget(self.submit_button)

        margin_x = round(64 * profile.ui_scale)
        margin_y = round(48 * profile.ui_scale)
        layout = create_grid(
            spacing=round(16 * profile.ui_scale),
            margins=(margin_x, margin_y, margin_x, margin_y),
        )
        self.setLayout(layout)
        add_widget(layout, self.form_panel, 0, 3, 6)
        layout.setRowStretch(0, 1)

    def set_loading(self, is_loading: bool) -> None:
        self.submit_button.setEnabled(not is_loading)
        self.submit_button.setText("Salvando..." if is_loading else "Salvar senha")

    def set_error(self, message: str) -> None:
        language = normalize_language(
            str(QSettings("PRO CORE", "PRO CORE").value("appearance/language", "pt-BR") or "pt-BR")
        )
        self.error_label.setText(translate_ui_text(message, language))

    def clear_form(self) -> None:
        self.current_password_input.clear()
        self.new_password_input.clear()
        self.confirm_password_input.clear()
        self.error_label.clear()
        self.set_loading(False)

    def _request_change(self) -> None:
        current_password = self.current_password_input.text()
        new_password = self.new_password_input.text()
        confirm_password = self.confirm_password_input.text()

        if not current_password or not new_password or not confirm_password:
            self.set_error("Preencha todos os campos.")
            return

        if len(new_password) < 8:
            self.set_error("A nova senha deve ter pelo menos 8 caracteres.")
            return

        if new_password != confirm_password:
            self.set_error("A confirmacao da senha nao confere.")
            return

        self.set_error("")
        self.password_change_requested.emit(current_password, new_password)
