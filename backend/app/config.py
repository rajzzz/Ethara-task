from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Ethara API"
    environment: str = "development"

    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/ethara"
    frontend_url: str = "http://localhost:3000"

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
