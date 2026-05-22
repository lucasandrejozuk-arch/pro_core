from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlsplit, urlunsplit

import httpx


@dataclass(frozen=True)
class BackendHealthStatus:
    is_connected: bool
    message: str


def health_url_from_api_base(api_base_url: str) -> str:
    parsed = urlsplit(api_base_url.rstrip("/"))
    path = parsed.path.rstrip("/")
    for suffix in ("/api/v1", "/api"):
        if path.endswith(suffix):
            path = path[: -len(suffix)]
            break
    health_path = f"{path}/health" if path else "/health"
    return urlunsplit((parsed.scheme, parsed.netloc, health_path, "", ""))


class BackendHealthProbe:
    def __init__(
        self,
        api_base_url: str,
        timeout: float = 0.8,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self.health_url = health_url_from_api_base(api_base_url)
        self._client = httpx.Client(timeout=timeout, transport=transport)

    def close(self) -> None:
        self._client.close()

    def check(self) -> BackendHealthStatus:
        try:
            response = self._client.get(self.health_url)
        except httpx.TimeoutException:
            return BackendHealthStatus(False, "Backend: sem resposta")
        except httpx.HTTPError:
            return BackendHealthStatus(False, "Backend: desconectado")

        if response.status_code != 200:
            return BackendHealthStatus(False, f"Backend: erro {response.status_code}")

        try:
            payload = response.json()
        except ValueError:
            return BackendHealthStatus(False, "Backend: resposta invalida")

        if str(payload.get("status") or "").lower() == "ok":
            return BackendHealthStatus(True, "Backend: conectado")

        return BackendHealthStatus(False, "Backend: health degradado")

