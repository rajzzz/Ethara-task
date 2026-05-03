from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Ethara API"
    environment: str = "development"

    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/ethara"
    frontend_url: str = "http://localhost:3000"
    cors_allowed_origins: str = ""
    cors_allow_origin_regex: str | None = None

    jwt_secret_key: str = "change-me-access-secret"
    jwt_refresh_secret_key: str = "change-me-refresh-secret"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    cookie_domain: str | None = None
    cookie_secure: bool = False


settings = Settings()


def normalized_database_url(database_url: str) -> str:
    # Railway often provides postgres:// or postgresql:// URLs.
    # Force SQLAlchemy to use the psycopg v3 driver installed in this project.
    if database_url.startswith("postgres://"):
        return database_url.replace("postgres://", "postgresql+psycopg://", 1)
    if database_url.startswith("postgresql://") and not database_url.startswith("postgresql+"):
        return database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    return database_url


def normalized_origin(origin: str) -> str:
    return origin.strip().rstrip("/")


def resolved_cors_origins() -> list[str]:
    origins = [normalized_origin(settings.frontend_url)]
    if settings.cors_allowed_origins:
        extras = [
            normalized_origin(origin)
            for origin in settings.cors_allowed_origins.split(",")
            if origin.strip()
        ]
        origins.extend(extras)

    # Preserve order while removing duplicates.
    deduped: list[str] = []
    for origin in origins:
        if origin and origin not in deduped:
            deduped.append(origin)
    return deduped
