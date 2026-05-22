from __future__ import annotations

from PySide6.QtCore import QSettings

from frontend.app.core.i18n import translate_ui_text


class ApiError(Exception):
    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code

    @property
    def display_message(self) -> str:
        language = str(
            QSettings("PRO CORE", "PRO CORE").value("appearance/language", "pt-BR") or "pt-BR"
        )
        translated = translate_ui_text(self.message, language)
        if self.status_code is None:
            return translated
        status_prefix = "Error" if language == "en-US" else "Erro"
        return f"{status_prefix} {self.status_code}: {translated}"
