from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "integrador-backend"
    version: str = "0.1.0"
    environment: str = "development"
    database_url: str = "postgresql+asyncpg://integrador:integrador@localhost:5432/integrador"
    search_backend: str = "simple"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
