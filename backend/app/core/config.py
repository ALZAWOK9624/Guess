from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://guess:guess_password@localhost:5432/guess"

    # JWT Authentication — ⚠️ MUST change for production!
    secret_key: str = "change-me-to-a-random-secret-key"
    jwt_secret: str = "change-me-to-a-different-random-secret"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # CORS
    cors_origins: List[str] = ["http://localhost:5173"]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
