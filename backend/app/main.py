from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from backend.app.api.v1.router import api_router
from backend.app.core.config import get_settings

APP_NAME = "PRO CORE"
APP_VERSION = "0.1.0"


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=APP_NAME,
        version=APP_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://127.0.0.1", "http://localhost"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health", tags=["system"])
    def health_check() -> dict[str, str]:
        return {
            "app": APP_NAME,
            "version": APP_VERSION,
            "environment": settings.pro_core_env,
            "status": "ok",
        }

    @app.get("/customer-portal", response_class=HTMLResponse, tags=["customer-portal"])
    def customer_portal() -> HTMLResponse:
        portal_path = Path(__file__).resolve().parent / "web" / "customer_portal.html"
        return HTMLResponse(portal_path.read_text(encoding="utf-8"))

    app.include_router(api_router)

    return app


app = create_app()
