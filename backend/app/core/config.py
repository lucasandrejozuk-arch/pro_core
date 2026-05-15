from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    pro_core_env: str = Field(default="development")
    pro_core_api_host: str = Field(default="127.0.0.1")
    pro_core_api_port: int = Field(default=8000)
    pro_core_secret_key: str = Field(default="change-me-before-production-pro-core-secret-key")
    pro_core_access_token_expire_minutes: int = Field(default=480)
    pro_core_bcrypt_rounds: int = Field(default=12, ge=4, le=14)

    postgres_db: str = Field(default="pro_core")
    postgres_user: str = Field(default="pro_core")
    postgres_password: str = Field(default="pro_core_dev_password")
    postgres_host: str = Field(default="127.0.0.1")
    postgres_port: int = Field(default=15432)

    database_url: str | None = Field(default=None)

    pro_core_backup_enabled: bool = Field(default=True)
    pro_core_backup_interval_hours: int = Field(default=24)
    pro_core_storage_dir: str = Field(default="storage")

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
