from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET_KEY: str = "CHANGE_THIS_TO_A_LONG_RANDOM_SECRET"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    STORAGE_ROOT: Path = Path("storage")
    FERNET_KEY: str | None = None
    MAX_UPLOAD_SIZE_BYTES: int = 25 * 1024 * 1024

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        extra="ignore",
    )


settings = Settings()
