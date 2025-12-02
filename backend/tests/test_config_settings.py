"""
Тесты для конфигурации приложения
"""

from src.app.setup.config.settings import Settings, get_settings


class TestSettings:
    """Тесты для настроек приложения"""

    def test_settings_has_required_attributes(self):
        """Тест наличия необходимых атрибутов в настройках"""
        settings = Settings()

        assert hasattr(settings, "ENVIRONMENT")
        assert hasattr(settings, "DEBUG")
        assert hasattr(settings, "PROJECT_NAME")
        assert hasattr(settings, "VERSION")
        assert hasattr(settings, "BACKEND_PORT")
        assert hasattr(settings, "DB_HOST")
        assert hasattr(settings, "DB_PORT")
        assert hasattr(settings, "DB_USER")
        assert hasattr(settings, "DB_PASSWORD")
        assert hasattr(settings, "DB_NAME")
        assert hasattr(settings, "DB_ECHO")
        assert hasattr(settings, "CORS_ORIGINS")
        assert hasattr(settings, "API_NINJAS_KEY")
        assert hasattr(settings, "API_NINJAS_BASE_URL")

    def test_database_url_property(self):
        """Тест формирования строки подключения к БД"""
        settings = Settings()
        db_url = settings.database_url

        assert "postgresql+asyncpg://" in db_url
        assert settings.DB_USER in db_url
        assert settings.DB_PASSWORD in db_url
        assert settings.DB_HOST in db_url
        assert settings.DB_PORT in db_url
        assert settings.DB_NAME in db_url

    def test_get_settings_cached(self):
        """Тест кэширования настроек"""
        settings1 = get_settings()
        settings2 = get_settings()

        assert settings1 is settings2
