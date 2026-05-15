from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class AppSession:
    access_token: str | None = None
    user: dict[str, Any] = field(default_factory=dict)
    login_at: datetime | None = None

    @property
    def is_authenticated(self) -> bool:
        return bool(self.access_token and self.user)

    def set_authentication(self, access_token: str, user: dict[str, Any]) -> None:
        self.access_token = access_token
        self.user = user
        self.login_at = datetime.now()

    def update_user(self, user: dict[str, Any]) -> None:
        self.user = user

    def clear(self) -> None:
        self.access_token = None
        self.login_at = None
        self.user.clear()
