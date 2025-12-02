"""
Конфигурация pytest и фикстуры для тестирования
"""

from collections.abc import AsyncGenerator
from datetime import UTC, datetime
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from src.app.domain.entities.api_data import ApiDataEntity
from src.app.setup.app_factory import app


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Асинхронный клиент для тестирования HTTP запросов"""
    host, port = "127.0.0.1", "9000"
    async with AsyncClient(
        transport=ASGITransport(app=app, client=(host, port)),
        base_url="http://test",
    ) as client:
        yield client


@pytest.fixture
def sample_api_data_entity() -> ApiDataEntity:
    """Фикстура для создания тестовой сущности ApiDataEntity"""
    return ApiDataEntity(
        id=uuid4(),
        source="test_source",
        title="Test Title",
        content="Test Content",
        external_id="123",
        fetched_at=datetime.now(UTC),
        created_at=datetime.now(UTC),
    )


@pytest.fixture
def mock_api_response() -> dict:
    """Фикстура для мокового ответа от внешнего API"""
    return {
        "number": 42,
        "text": "42 is the answer to the ultimate question of life, the universe, and everything.",
    }
