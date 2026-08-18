from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_ENV_FILE = Path(__file__).resolve().parents[4] / ".env"


class Settings(BaseSettings):
    app_name: str = "Imanol Data & AI Campus API"
    database_url: str = (
        "postgresql+psycopg://campus:campus_dev_password@localhost:5432/campus"
    )

    model_config = SettingsConfigDict(env_file=ROOT_ENV_FILE, env_prefix="")


@lru_cache
def get_settings() -> Settings:
    return Settings()
