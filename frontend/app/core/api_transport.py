from __future__ import annotations

from typing import Any

import httpx

from frontend.app.core.api_errors import ApiError


class ApiTransportMixin:
    def __init__(
        self,
        base_url: str,
        timeout: float = 10.0,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self._client = httpx.Client(
            base_url=base_url.rstrip("/") + "/",
            timeout=timeout,
            transport=transport,
        )

    def close(self) -> None:
        self._client.close()

    def _request_list(
        self,
        method: str,
        path: str,
        access_token: str | None = None,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        data = self._request(method, path, access_token=access_token, **kwargs)
        if not isinstance(data, list):
            raise ApiError("Resposta inesperada do backend.")

        return data

    def _request(
        self,
        method: str,
        path: str,
        access_token: str | None = None,
        **kwargs: Any,
    ) -> Any:
        headers = dict(kwargs.pop("headers", {}))
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"

        try:
            response = self._client.request(method, path, headers=headers, **kwargs)
        except httpx.ConnectError as exc:
            raise ApiError("Nao foi possivel conectar ao backend.") from exc
        except httpx.TimeoutException as exc:
            raise ApiError("Tempo limite excedido ao conectar ao backend.") from exc
        except httpx.HTTPError as exc:
            raise ApiError(f"Falha de comunicacao com o backend: {exc}") from exc

        if response.is_error:
            raise ApiError(self._extract_error_message(response), response.status_code)

        if response.status_code == 204 or not response.content:
            return None

        return response.json()

    def _download(
        self,
        method: str,
        path: str,
        access_token: str | None = None,
        **kwargs: Any,
    ) -> bytes:
        headers = dict(kwargs.pop("headers", {}))
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"

        try:
            response = self._client.request(method, path, headers=headers, **kwargs)
        except httpx.ConnectError as exc:
            raise ApiError("Nao foi possivel conectar ao backend.") from exc
        except httpx.TimeoutException as exc:
            raise ApiError("Tempo limite excedido ao conectar ao backend.") from exc
        except httpx.HTTPError as exc:
            raise ApiError(f"Falha de comunicacao com o backend: {exc}") from exc

        if response.is_error:
            raise ApiError(self._extract_error_message(response), response.status_code)

        return response.content

    @staticmethod
    def _extract_error_message(response: httpx.Response) -> str:
        try:
            body = response.json()
        except ValueError:
            return response.text or "Erro inesperado do backend."

        detail = body.get("detail")
        if isinstance(detail, str):
            return detail

        if isinstance(detail, list) and detail:
            first_error = detail[0]
            if isinstance(first_error, dict) and "msg" in first_error:
                return str(first_error["msg"])

        return "Erro inesperado do backend."
