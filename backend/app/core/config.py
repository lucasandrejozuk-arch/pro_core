from functools import lru_cache

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_SECRET_KEY = "change-me-before-production-pro-core-secret-key"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    pro_core_env: str = Field(default="development")
    pro_core_api_host: str = Field(default="127.0.0.1")
    pro_core_api_port: int = Field(default=8000)
    pro_core_secret_key: str = Field(default=DEFAULT_SECRET_KEY)
    pro_core_access_token_expire_minutes: int = Field(default=480)
    pro_core_bcrypt_rounds: int = Field(default=12, ge=4, le=14)
    pro_core_login_rate_limit_attempts: int = Field(default=5, ge=2, le=20)
    pro_core_login_rate_limit_window_seconds: int = Field(default=300, ge=30, le=3600)
    pro_core_public_rate_limit_attempts: int = Field(default=5, ge=2, le=30)
    pro_core_public_rate_limit_window_seconds: int = Field(default=300, ge=30, le=3600)
    pro_core_allowed_cors_origins: list[str] = Field(
        default_factory=lambda: ["http://127.0.0.1", "http://localhost"]
    )

    postgres_db: str = Field(default="pro_core")
    postgres_user: str = Field(default="pro_core")
    postgres_password: str = Field(default="pro_core_dev_password")
    postgres_host: str = Field(default="127.0.0.1")
    postgres_port: int = Field(default=15432)

    database_url: str | None = Field(default=None)

    pro_core_backup_enabled: bool = Field(default=True)
    pro_core_backup_interval_hours: int = Field(default=24)
    pro_core_backup_command_timeout_seconds: int = Field(default=300, ge=15, le=3600)
    pro_core_storage_dir: str = Field(default="storage")
    pro_core_max_upload_bytes: int = Field(default=25 * 1024 * 1024, ge=1024)
    pro_core_allowed_document_extensions: set[str] = Field(
        default_factory=lambda: {
            ".csv",
            ".doc",
            ".docx",
            ".jpg",
            ".jpeg",
            ".pdf",
            ".png",
            ".txt",
            ".xls",
            ".xlsx",
        }
    )

    @model_validator(mode="after")
    def validate_production_security(self) -> "Settings":
        is_production = self.pro_core_env.strip().lower() in {"production", "prod"}
        has_weak_secret = (
            self.pro_core_secret_key == DEFAULT_SECRET_KEY or len(self.pro_core_secret_key) < 32
        )
        if is_production and has_weak_secret:
            raise ValueError(
                "PRO_CORE_SECRET_KEY must be changed and contain at least 32 characters "
                "in production."
            )
        return self

    @property
    def sqlalchemy_database_url(self) -> str:
        if self.database_url:
            return self.database_url

        return (
            "postgresql+psycopg://"
            f"{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
