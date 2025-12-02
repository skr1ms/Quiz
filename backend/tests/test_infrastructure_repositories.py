"""
Тесты для репозиториев
"""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from src.app.domain.entities.api_data import ApiDataEntity
from src.app.infrastructure.persistence.models.api_data import ApiDataModel
from src.app.infrastructure.persistence.repositories.api_data_repository import ApiDataRepository


class TestApiDataRepository:
    """Тесты для репозитория ApiDataRepository"""

    @pytest.fixture
    def mock_session(self):
        """Фикстура для моковой сессии БД"""
        session = AsyncMock()
        session.commit = AsyncMock()
        session.refresh = AsyncMock()
        session.add = MagicMock()
        return session

    @pytest.fixture
    def repository(self, mock_session):
        """Фикстура для создания репозитория"""
        return ApiDataRepository(mock_session)

    @pytest.mark.asyncio
    async def test_create_entity(self, repository, mock_session):
        """Тест создания новой записи"""
        entity_id = uuid4()
        fetched_at = datetime.now(UTC)
        entity = ApiDataEntity(
            id=entity_id,
            source="test_source",
            title="Test Title",
            content="Test Content",
            external_id="123",
            fetched_at=fetched_at,
        )

        mock_model = MagicMock(spec=ApiDataModel)
        mock_model.id = entity_id
        mock_session.add.return_value = None
        mock_session.refresh = AsyncMock()

        def refresh_side_effect(model):
            model.id = entity_id

        mock_session.refresh.side_effect = refresh_side_effect

        result = await repository.create(entity)

        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        assert result.id == entity_id

    @pytest.mark.asyncio
    async def test_get_by_id_found(self, repository, mock_session):
        """Тест получения записи по ID"""
        entity_id = uuid4()
        mock_model = MagicMock(spec=ApiDataModel)
        mock_model.id = entity_id
        mock_model.source = "test_source"
        mock_model.title = "Test Title"
        mock_model.content = "Test Content"
        mock_model.external_id = "123"
        mock_model.fetched_at = datetime.now(UTC)
        mock_model.created_at = datetime.now(UTC)
        mock_model.updated_at = None

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_model

        mock_execute = AsyncMock(return_value=mock_result)
        mock_session.execute = mock_execute

        result = await repository.get_by_id(entity_id)

        assert result is not None
        assert result.id == entity_id
        assert result.source == "test_source"

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, repository, mock_session):
        """Тест получения несуществующей записи по ID"""
        entity_id = uuid4()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None

        mock_execute = AsyncMock(return_value=mock_result)
        mock_session.execute = mock_execute

        result = await repository.get_by_id(entity_id)

        assert result is None

    @pytest.mark.asyncio
    async def test_get_all_with_pagination(self, repository, mock_session):
        """Тест получения всех записей с пагинацией"""
        mock_models = [
            MagicMock(
                spec=ApiDataModel,
                id=uuid4(),
                source="test_source",
                title=f"Test Title {i}",
                content=f"Test Content {i}",
                external_id=None,
                fetched_at=datetime.now(UTC),
                created_at=datetime.now(UTC),
                updated_at=None,
            )
            for i in range(3)
        ]

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_models

        mock_execute = AsyncMock(return_value=mock_result)
        mock_session.execute = mock_execute

        result = await repository.get_all(limit=3, offset=0)

        assert len(result) == 3
        assert all(isinstance(item, ApiDataEntity) for item in result)

    @pytest.mark.asyncio
    async def test_count(self, repository, mock_session):
        """Тест подсчета количества записей"""
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 10

        mock_execute = AsyncMock(return_value=mock_result)
        mock_session.execute = mock_execute

        result = await repository.count()

        assert result == 10
