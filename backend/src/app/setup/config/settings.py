"""
Конфигурация приложения с настройками из переменных окружения
"""

import os
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Настройки приложения из переменных окружения"""

    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "local")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "FastAPI Project")
    VERSION: str = os.getenv("VERSION", "1.0.0")
    BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", "8081"))

    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_USER: str = os.getenv("DB_USER", "user")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "password")
    DB_NAME: str = os.getenv("DB_NAME", "dbname")

    @property
    def database_url(self) -> str:
        """Формирование строки подключения к БД"""
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    DB_ECHO: bool = os.getenv("DB_ECHO", "false").lower() == "true"

    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "*")

    API_NINJAS_KEY: str = os.getenv("API_NINJAS", "")
    API_NINJAS_BASE_URL: str = os.getenv("API_NINJAS_BASE_URL", "https://api.api-ninjas.com/v1")


@lru_cache
def get_settings() -> Settings:
    """Получение кэшированного экземпляра настроек"""
    return Settings()
