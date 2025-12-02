"""
Тесты для запросов приложения
"""

from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.app.application.queries.get_api_data import GetApiDataQuery
from src.app.domain.entities.api_data import ApiDataEntity


class TestGetApiDataQuery:
    """Тесты для запросов получения данных из БД"""

    @pytest.mark.asyncio
    async def test_get_by_id_success(self):
        """Тест успешного получения данных по ID"""
        mock_repository = AsyncMock()
        entity_id = uuid4()
        entity = ApiDataEntity(
            id=entity_id,
            source="test_source",
            title="Test Title",
            content="Test Content",
            external_id="123",
            fetched_at=datetime.now(UTC),
        )

        mock_repository.get_by_id.return_value = entity

        query = GetApiDataQuery(mock_repository)
        result = await query.get_by_id(entity_id)

        mock_repository.get_by_id.assert_called_once_with(entity_id)
        assert result == entity
        assert result.id == entity_id

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self):
        """Тест получения данных по несуществующему ID"""
        mock_repository = AsyncMock()
        entity_id = uuid4()

        mock_repository.get_by_id.return_value = None

        query = GetApiDataQuery(mock_repository)
        result = await query.get_by_id(entity_id)

        mock_repository.get_by_id.assert_called_once_with(entity_id)
        assert result is None

    @pytest.mark.asyncio
    async def test_get_all_with_pagination(self):
        """Тест получения всех данных с пагинацией"""
        mock_repository = AsyncMock()
        entities = [
            ApiDataEntity(
                id=uuid4(),
                source="test_source",
                title=f"Test Title {i}",
                content=f"Test Content {i}",
                fetched_at=datetime.now(UTC),
            )
            for i in range(3)
        ]

        mock_repository.get_all.return_value = entities
        mock_repository.count.return_value = 10

        query = GetApiDataQuery(mock_repository)
        items, total = await query.get_all(limit=3, offset=0)

        mock_repository.get_all.assert_called_once_with(limit=3, offset=0)
        mock_repository.count.assert_called_once()
        assert len(items) == 3
        assert total == 10

    @pytest.mark.asyncio
    async def test_get_all_default_pagination(self):
        """Тест получения всех данных с дефолтной пагинацией"""
        mock_repository = AsyncMock()
        entities = []

        mock_repository.get_all.return_value = entities
        mock_repository.count.return_value = 0

        query = GetApiDataQuery(mock_repository)
        items, total = await query.get_all()

        mock_repository.get_all.assert_called_once_with(limit=10, offset=0)
        assert len(items) == 0
        assert total == 0

    @pytest.mark.asyncio
    async def test_get_by_source(self):
        """Тест получения данных по источнику"""
        mock_repository = AsyncMock()
        entities = [
            ApiDataEntity(
                id=uuid4(),
                source="test_source",
                title="Test Title",
                content="Test Content",
                fetched_at=datetime.now(UTC),
            )
        ]

        mock_repository.get_by_source.return_value = entities

        query = GetApiDataQuery(mock_repository)
        result = await query.get_by_source("test_source", limit=10, offset=0)

        mock_repository.get_by_source.assert_called_once_with("test_source", limit=10, offset=0)
        assert len(result) == 1
        assert result[0].source == "test_source"
