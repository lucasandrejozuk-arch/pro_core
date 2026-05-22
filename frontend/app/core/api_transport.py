from __future__ import annotations

import time
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

        response = self._request_with_redundancy(method, path, headers=headers, **kwargs)

        if response.is_error:
            raise ApiError(self._extract_error_message(response), response.status_code)

        if response.status_code == 204 or not response.content:
            return None

        try:
            return response.json()
        except ValueError as exc:
            raise ApiError("Resposta invalida do backend.", response.status_code) from exc

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

        response = self._request_with_redundancy(method, path, headers=headers, **kwargs)

        if response.is_error:
            raise ApiError(self._extract_error_message(response), response.status_code)

        return response.content

    def _request_with_redundancy(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> httpx.Response:
        normalized_method = str(method or "GET").upper()
        retries = 2 if normalized_method in {"GET", "HEAD", "OPTIONS", "DELETE"} else 0
        attempt = 0

        while True:
            try:
                response = self._client.request(normalized_method, path, **kwargs)
            except httpx.ConnectError as exc:
                if attempt < retries:
                    attempt += 1
                    time.sleep(0.12 * attempt)
                    continue
                raise ApiError("Nao foi possivel conectar ao backend.") from exc
            except httpx.TimeoutException as exc:
                if attempt < retries:
                    attempt += 1
                    time.sleep(0.12 * attempt)
                    continue
                raise ApiError("Tempo limite excedido ao conectar ao backend.") from exc
            except httpx.RequestError as exc:
                raise ApiError(f"Falha de comunicacao com o backend: {exc}") from exc

            if response.status_code >= 500 and attempt < retries:
                attempt += 1
                time.sleep(0.12 * attempt)
                continue

            return response

    @staticmethod
    def _extract_error_message(response: httpx.Response) -> str:
        try:
            body = response.json()
        except ValueError:
            return _fallback_error_message(response.status_code, response.text)

        detail = body.get("detail")
        if isinstance(detail, str):
            return _translate_error_message(detail, response.status_code)

        if isinstance(detail, list) and detail:
            first_error = detail[0]
            if isinstance(first_error, dict) and "msg" in first_error:
                location = first_error.get("loc")
                field = ".".join(str(part) for part in location or [] if part != "body")
                prefix = f"{field}: " if field else ""
                return prefix + _translate_error_message(
                    str(first_error["msg"]),
                    response.status_code,
                )

        return _fallback_error_message(response.status_code)


def _fallback_error_message(status_code: int, raw_message: str = "") -> str:
    raw = raw_message.strip()
    if status_code >= 500:
        return "Falha interna no servidor. Tente novamente ou acione o suporte."
    if status_code == 404:
        return "Registro nao encontrado."
    if status_code == 403:
        return "Acesso negado para esta operacao."
    if status_code == 401:
        return "Sessao invalida ou expirada."
    if status_code == 422:
        return "Dados invalidos. Revise os campos informados."
    return raw or "Erro inesperado ao processar a solicitacao."


def _translate_error_message(message: str, status_code: int) -> str:
    normalized = message.strip()
    if status_code >= 500 or _looks_internal(normalized):
        return _fallback_error_message(status_code)
    translations = {
        "Invalid email or password.": "Email ou senha invalidos.",
        "Service order not found.": "Ordem de servico nao encontrada.",
        "Customer not found.": "Cliente nao encontrado.",
        "Equipment not found.": "Equipamento nao encontrado.",
        "User not found.": "Usuario nao encontrado.",
        "Company not found.": "Empresa nao encontrada.",
        "Internal Server Error": "Falha interna no servidor. Tente novamente ou acione o suporte.",
    }
    if normalized in translations:
        return translations[normalized]
    if normalized.startswith("Input should be "):
        return "Valor invalido para este campo. Atualize os dados e tente novamente."
    generic_server_errors = {"internal error server", "internal server error"}
    if status_code >= 500 and normalized.lower() in generic_server_errors:
        return translations["Internal Server Error"]
    return normalized or _fallback_error_message(status_code)


def _looks_internal(message: str) -> bool:
    lowered = message.lower()
    internal_markers = (
        "traceback",
        "sqlalchemy",
        "psycopg",
        "sqlite",
        "starlette",
        "fastapi",
        "exception",
        'file "',
        "c:\\",
    )
    return any(marker in lowered for marker in internal_markers)
