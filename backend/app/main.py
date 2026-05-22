from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from backend.app.api.v1.router import api_router
from backend.app.core.config import get_settings

APP_NAME = "PRO CORE"
APP_VERSION = "0.1.0"


def create_app() -> FastAPI:
    settings = get_settings()
    is_production = settings.pro_core_env.strip().lower() in {"production", "prod"}

    app = FastAPI(
        title=APP_NAME,
        version=APP_VERSION,
        docs_url=None if is_production else "/docs",
        redoc_url=None if is_production else "/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.pro_core_allowed_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def add_security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "no-referrer")
        response.headers.setdefault("Cache-Control", "no-store")
        if request.url.path == "/customer-portal":
            response.headers.setdefault(
                "Content-Security-Policy",
                "default-src 'self'; script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; frame-ancestors 'none'; object-src 'none'",
            )
        else:
            response.headers.setdefault(
                "Content-Security-Policy",
                "default-src 'self'; frame-ancestors 'none'; object-src 'none'",
            )
        if is_production:
            response.headers.setdefault(
                "Strict-Transport-Security",
                "max-age=31536000; includeSubDomains",
            )
        return response

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
