from __future__ import annotations


class ApiError(Exception):
    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code

    @property
    def display_message(self) -> str:
        if self.status_code is None:
            return self.message
        return f"[HTTP-{self.status_code}] {self.message}"
