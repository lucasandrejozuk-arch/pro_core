from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class FrontendSettings:
    api_base_url: str
    manage_backend_process: bool


def _env_flag(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "on"}


def get_frontend_settings() -> FrontendSettings:
    load_dotenv()
    return FrontendSettings(
        api_base_url=os.getenv("PRO_CORE_API_BASE_URL", "http://127.0.0.1:8000/api/v1"),
        manage_backend_process=_env_flag("PRO_CORE_MANAGE_BACKEND"),
    )

