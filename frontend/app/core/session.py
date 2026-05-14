from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AppSession:
    access_token: str | None = None
    user: dict[str, Any] = field(default_factory=dict)

    @property
    def is_authenticated(self) -> bool:
        return bool(self.access_token and self.user)

    def set_authentication(self, access_token: str, user: dict[str, Any]) -> None:
        self.access_token = access_token
        self.user = user

    def update_user(self, user: dict[str, Any]) -> None:
        self.user = user

    def clear(self) -> None:
        self.access_token = None
        self.user.clear()

