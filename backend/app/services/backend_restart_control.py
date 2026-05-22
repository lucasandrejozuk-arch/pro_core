from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from backend.app.models.enums import UserRole
from backend.app.services.configuration import get_setting_value, set_setting_value
from backend.app.services.users import authenticate_user, get_company_user_by_email

BACKEND_RESTART_ALLOWED_EMAILS_KEY = "ops.backend_restart_allowed_emails"
BACKEND_RESTART_NOTICE_KEY = "ops.backend_restart_notice"
BACKEND_RESTART_LAST_REQUESTED_AT_KEY = "ops.backend_restart_last_requested_at"
BACKEND_RESTART_COOLDOWN_SECONDS = 3


def get_backend_restart_allowed_emails(db: Session, company_id: uuid.UUID) -> list[str]:
    raw = get_setting_value(db, company_id, BACKEND_RESTART_ALLOWED_EMAILS_KEY) or ""
    return _normalize_email_list(raw.split(","))


def set_backend_restart_allowed_emails(
    db: Session,
    company_id: uuid.UUID,
    emails: list[str],
) -> list[str]:
    normalized = _normalize_email_list(emails)
    set_setting_value(
        db,
        company_id,
        BACKEND_RESTART_ALLOWED_EMAILS_KEY,
        ",".join(normalized),
        "Contas permitidas para reinicio autorizado do backend.",
    )
    db.commit()
    return normalized


def authorize_backend_restart(
    db: Session,
    operator_email: str,
    admin_email: str,
    admin_password: str,
    reason_type: str,
    custom_reason: str | None,
) -> dict[str, str]:
    operator_email_normalized = _normalize_email(operator_email)
    admin_email_normalized = _normalize_email(admin_email)

    admin_user = authenticate_user(db, admin_email_normalized, admin_password)
    if admin_user is None:
        raise PermissionError("Senha do administrador invalida.")
    if admin_user.role != UserRole.ADMIN:
        raise PermissionError("A confirmacao deve ser feita com uma conta administradora.")

    operator_user = get_company_user_by_email(db, admin_user.company_id, operator_email_normalized)
    if operator_user is None or not operator_user.is_active:
        raise PermissionError("Conta operadora nao encontrada ou inativa.")

    allowed_emails = set(get_backend_restart_allowed_emails(db, admin_user.company_id))
    operator_is_admin = operator_user.role == UserRole.ADMIN
    operator_allowed = operator_is_admin or operator_user.email in allowed_emails
    if not operator_allowed:
        raise PermissionError(
            "Esta conta nao possui permissao para reiniciar o backend. "
            "Solicite ao administrador a liberacao desta conta."
        )

    now = datetime.now(UTC)
    _validate_cooldown(db, admin_user.company_id, now)
    reason_text = _build_reason(reason_type, custom_reason)
    notice_id = str(uuid.uuid4())
    notice = {
        "id": notice_id,
        "created_at": now.isoformat(),
        "operator_email": operator_user.email,
        "authorized_by_admin_email": admin_user.email,
        "reason_type": reason_type,
        "reason": reason_text,
    }

    set_setting_value(
        db,
        admin_user.company_id,
        BACKEND_RESTART_NOTICE_KEY,
        json.dumps(notice, ensure_ascii=True),
        "Ultimo aviso de reinicio programado do backend.",
    )
    set_setting_value(
        db,
        admin_user.company_id,
        BACKEND_RESTART_LAST_REQUESTED_AT_KEY,
        now.isoformat(),
        "Controle de cooldown para solicitacoes de reinicio do backend.",
    )
    db.commit()
    return notice


def get_latest_backend_restart_notice(db: Session, company_id: uuid.UUID) -> dict[str, str] | None:
    raw = get_setting_value(db, company_id, BACKEND_RESTART_NOTICE_KEY)
    if not raw:
        return None
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return None
    if not isinstance(parsed, dict):
        return None

    notice_id = str(parsed.get("id") or "").strip()
    reason = str(parsed.get("reason") or "").strip()
    created_at = str(parsed.get("created_at") or "").strip()
    if not notice_id or not reason or not created_at:
        return None

    return {
        "id": notice_id,
        "created_at": created_at,
        "operator_email": str(parsed.get("operator_email") or "").strip(),
        "authorized_by_admin_email": str(parsed.get("authorized_by_admin_email") or "").strip(),
        "reason_type": str(parsed.get("reason_type") or "").strip(),
        "reason": reason,
    }


def _validate_cooldown(db: Session, company_id: uuid.UUID, now: datetime) -> None:
    raw_last = get_setting_value(db, company_id, BACKEND_RESTART_LAST_REQUESTED_AT_KEY)
    if not raw_last:
        return
    try:
        last_dt = datetime.fromisoformat(raw_last)
    except ValueError:
        return
    if last_dt.tzinfo is None:
        last_dt = last_dt.replace(tzinfo=UTC)
    elapsed = (now - last_dt).total_seconds()
    if elapsed < BACKEND_RESTART_COOLDOWN_SECONDS:
        remaining = int(BACKEND_RESTART_COOLDOWN_SECONDS - elapsed) + 1
        raise RuntimeError(f"Aguarde {remaining}s para solicitar novo reinicio do backend.")


def _build_reason(reason_type: str, custom_reason: str | None) -> str:
    normalized = reason_type.strip().lower()
    if normalized == "maintenance":
        return "Manutencao programada"
    if normalized == "hang":
        return "Backend travado"
    if normalized != "other":
        raise ValueError("Motivo de reinicio invalido.")

    custom = str(custom_reason or "").strip()
    if len(custom) < 4:
        raise ValueError("Informe um motivo personalizado com pelo menos 4 caracteres.")
    return custom


def _normalize_email_list(values: list[str]) -> list[str]:
    normalized = []
    seen = set()
    for value in values:
        email = _normalize_email(value)
        if not email or email in seen:
            continue
        seen.add(email)
        normalized.append(email)
    return normalized


def _normalize_email(value: str) -> str:
    return value.strip().lower()
