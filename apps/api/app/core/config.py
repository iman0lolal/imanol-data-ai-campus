from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Imanol Data & AI Campus API"
    database_url: str = (
        "postgresql+psycopg://campus:campus_dev_password@localhost:5432/campus"
    )

    model_config = SettingsConfigDict(env_file=".env", env_prefix="")


@lru_cache
def get_settings() -> Settings:
    return Settings()
