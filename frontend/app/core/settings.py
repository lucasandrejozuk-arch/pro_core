from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class FrontendSettings:
    api_base_url: str


def get_frontend_settings() -> FrontendSettings:
    load_dotenv()
    return FrontendSettings(
        api_base_url=os.getenv("PRO_CORE_API_BASE_URL", "http://127.0.0.1:8000/api/v1")
    )

