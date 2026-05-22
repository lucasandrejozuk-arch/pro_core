from __future__ import annotations

from frontend.app.core.i18n import translate_ui_text


class ApiError(Exception):
    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code

    @property
    def display_message(self) -> str:
        translated = translate_ui_text(self.message, "pt-BR")
        if self.status_code is None:
            return translated
        return f"Erro {self.status_code}: {translated}"
