from __future__ import annotations

from datetime import UTC, datetime, timedelta
from functools import lru_cache
from typing import Any

import bcrypt
import jwt
from jwt import InvalidTokenError

from backend.app.core.config import get_settings

JWT_ALGORITHM = "HS256"


def validate_password_strength(password: str) -> None:
    if len(password) < 8:
        raise ValueError("Password must contain at least 8 characters.")
    if not any(character.islower() for character in password):
        raise ValueError("Password must contain at least one lowercase letter.")
    if not any(character.isupper() for character in password):
        raise ValueError("Password must contain at least one uppercase letter.")
    if not any(character.isdigit() for character in password):
        raise ValueError("Password must contain at least one number.")


def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")
    return bcrypt.hashpw(
        password_bytes,
        bcrypt.gensalt(rounds=get_settings().pro_core_bcrypt_rounds),
    ).decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:
        return False


def verify_password_for_missing_user(plain_password: str) -> None:
    settings = get_settings()
    verify_password(plain_password, _dummy_password_hash(settings.pro_core_bcrypt_rounds))


@lru_cache(maxsize=8)
def _dummy_password_hash(rounds: int) -> str:
    return bcrypt.hashpw(
        b"pro-core-missing-user-password",
        bcrypt.gensalt(rounds=rounds),
    ).decode("utf-8")


def create_access_token(subject: str, extra_claims: dict[str, Any] | None = None) -> str:
    settings = get_settings()
    expires_at = datetime.now(UTC) + timedelta(
        minutes=settings.pro_core_access_token_expire_minutes
    )
    payload: dict[str, Any] = {
        "sub": subject,
        "exp": expires_at,
        "iat": datetime.now(UTC),
        "type": "access",
    }

    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(payload, settings.pro_core_secret_key, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    settings = get_settings()

    try:
        payload = jwt.decode(token, settings.pro_core_secret_key, algorithms=[JWT_ALGORITHM])
    except InvalidTokenError as exc:
        raise ValueError("Invalid access token.") from exc

    if payload.get("type") != "access":
        raise ValueError("Invalid token type.")

    return payload
