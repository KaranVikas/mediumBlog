import os
from typing import List, Optional
from pydantic import PostgresDsn, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database configuration
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[SecretStr] = None
    POSTGRES_HOST: Optional[str] = None
    POSTGRES_PORT: Optional[int] = None
    POSTGRES_DB: Optional[str] = None

    # App configuration
    DOMAIN: Optional[str] = None
    ENVIRONMENT: Optional[str] = None
    BACKEND_CORS_ORIGINS: List[str] = []
    PROJECT_NAME: str = "Medium blog"
    SECRET_KEY: Optional[SecretStr] = None
    API_PREFIX: str = "/api"

    ALGORITHM: str = "HS256"  # Or "RS256" for asymmetric encryption
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Computed database URLs
    @property
    def async_db_url(self) -> PostgresDsn:
        return self._build_db_url("postgresql+asyncpg")

    @property
    def sync_db_url(self) -> PostgresDsn:
        return self._build_db_url("postgresql")

    def _build_db_url(self, driver: str) -> PostgresDsn:
        return PostgresDsn.build(
            scheme=driver,
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD.get_secret_value() if self.POSTGRES_PASSWORD else None,
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | List[str]) -> List[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    model_config = SettingsConfigDict(
        env_file=None,  # Explicitly disable .env file loading
        case_sensitive=True,  # Case-sensitive environment variables
        extra="forbid",  # Reject unexpected env variables
    )


settings = Settings()