from app.core.config import Settings


def test_environment_variables_override_dotenv(monkeypatch, tmp_path) -> None:
    dotenv_database_url = "postgresql+psycopg://from_dotenv:pass@localhost:5432/db"
    env_database_url = "postgresql+psycopg://from_env:pass@localhost:5432/db"
    (tmp_path / ".env").write_text(f"DATABASE_URL={dotenv_database_url}\n")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("DATABASE_URL", env_database_url)

    settings = Settings()

    assert settings.database_url == env_database_url
