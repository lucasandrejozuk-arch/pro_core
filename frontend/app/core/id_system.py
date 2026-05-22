from __future__ import annotations

import re
import secrets
from datetime import UTC, datetime

_PREFIX_BY_MODULE: dict[str, str] = {
    "customers": "CUS",
    "equipment": "EQP",
    "inventory": "INV",
    "service_orders": "OS",
    "sectors": "SEC",
    "users": "USR",
    "resource_access": "UAC",
    "password_resets": "PRQ",
    "audit_logs": "LOG",
}

_NON_ALNUM = re.compile(r"[^A-Z0-9]+")


def generate_entity_code(prefix: str) -> str:
    normalized_prefix = _normalize_prefix(prefix)
    now = datetime.now(UTC)
    stamp = now.strftime("%Y%m%d%H%M%S")
    random_suffix = secrets.token_hex(2).upper()
    return f"{normalized_prefix}-{stamp}-{random_suffix}"


def professional_record_id(module_key: str, record: dict) -> str:
    prefix = _PREFIX_BY_MODULE.get(module_key, "REC")

    explicit_candidates = []
    if module_key == "inventory":
        explicit_candidates.append(str(record.get("sku") or ""))
    if module_key == "service_orders":
        explicit_candidates.extend(
            [
                str(record.get("custom_id") or ""),
                str(record.get("code") or ""),
            ]
        )

    for candidate in explicit_candidates:
        token = _compact_token(candidate)
        if token:
            return f"{_normalize_prefix(prefix)}-{token}"

    raw_id = str(record.get("id") or record.get("user_id") or "")
    token = _compact_token(raw_id)
    if not token:
        token = secrets.token_hex(4).upper()

    return f"{_normalize_prefix(prefix)}-{token}"


def _normalize_prefix(prefix: str) -> str:
    cleaned = _NON_ALNUM.sub("", str(prefix or "").upper())
    return cleaned[:4] or "REC"


def _compact_token(value: str) -> str:
    cleaned = _NON_ALNUM.sub("", str(value or "").upper())
    if not cleaned:
        return ""
    return cleaned[:10]
