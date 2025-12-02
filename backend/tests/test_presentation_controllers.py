"""
Тесты для HTTP контроллеров
"""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import status

from src.app.domain.entities.api_data import ApiDataEntity
from src.app.infrastructure.persistence.repositories.api_data_repository import ApiDataRepository
from src.app.presentation.http.controllers.api_data_controller import (
    fetch_api_data,
    get_all_api_data,
    get_api_data_by_id,
)
from src.app.presentation.http.schemas.api_data import FetchApiDataRequest


class TestApiDataController:
    """Тесты для контроллера api_data"""

    @pytest.fixture
    def mock_repository(self):
        """Фикстура для мокового репозитория"""
        return AsyncMock(spec=ApiDataRepository)

    @pytest.mark.asyncio
    async def test_fetch_api_data_success(self, mock_repository):
        """Тест успешного получения данных из внешнего API"""
        entity_id = uuid4()
        entity = ApiDataEntity(
            id=entity_id,
            source="numbersapi",
            title="Факт о числе 42",
            content="42 is the answer",
            external_id="42",
            fetched_at=datetime.now(UTC),
        )

        mock_repository.create.return_value = entity

        command_mock = MagicMock()
        command_mock.execute = AsyncMock(return_value=entity)

        with patch(
            "src.app.presentation.http.controllers.api_data_controller.FetchApiDataCommand",
            return_value=command_mock,
        ):
            request = FetchApiDataRequest(number=42)
            result = await fetch_api_data(request, mock_repository)

            assert result.id == entity_id
            assert result.source == "numbersapi"
            assert result.title == "Факт о числе 42"

    @pytest.mark.asyncio
    async def test_fetch_api_data_error(self, mock_repository):
        """Тест обработки ошибки при получении данных"""
        from fastapi import HTTPException

        mock_repository.create.side_effect = Exception("API Error")

        command_mock = MagicMock()
        command_mock.execute = AsyncMock(side_effect=Exception("API Error"))

        with patch(
            "src.app.presentation.http.controllers.api_data_controller.FetchApiDataCommand",
            return_value=command_mock,
        ):
            request = FetchApiDataRequest(number=42)

            with pytest.raises(HTTPException) as exc_info:
                await fetch_api_data(request, mock_repository)

            assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    @pytest.mark.asyncio
    async def test_get_api_data_by_id_success(self, mock_repository):
        """Тест успешного получения данных по ID"""
        entity_id = uuid4()
        entity = ApiDataEntity(
            id=entity_id,
            source="test_source",
            title="Test Title",
            content="Test Content",
            fetched_at=datetime.now(UTC),
        )

        query_mock = MagicMock()
        query_mock.get_by_id = AsyncMock(return_value=entity)

        with patch(
            "src.app.presentation.http.controllers.api_data_controller.GetApiDataQuery",
            return_value=query_mock,
        ):
            result = await get_api_data_by_id(entity_id, mock_repository)

            assert result.id == entity_id
            assert result.source == "test_source"

    @pytest.mark.asyncio
    async def test_get_api_data_by_id_not_found(self, mock_repository):
        """Тест получения несуществующих данных по ID"""
        from fastapi import HTTPException

        entity_id = uuid4()

        query_mock = MagicMock()
        query_mock.get_by_id = AsyncMock(return_value=None)

        with patch(
            "src.app.presentation.http.controllers.api_data_controller.GetApiDataQuery",
            return_value=query_mock,
        ):
            with pytest.raises(HTTPException) as exc_info:
                await get_api_data_by_id(entity_id, mock_repository)

            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_get_all_api_data_with_pagination(self, mock_repository):
        """Тест получения всех данных с пагинацией"""
        from src.app.presentation.http.common.pagination import PaginationParams

        entities = [
            ApiDataEntity(
                id=uuid4(),
                source="test_source",
                title=f"Test Title {i}",
                content=f"Test Content {i}",
                fetched_at=datetime.now(UTC),
            )
            for i in range(2)
        ]

        query_mock = MagicMock()
        query_mock.get_all = AsyncMock(return_value=(entities, 10))

        with patch(
            "src.app.presentation.http.controllers.api_data_controller.GetApiDataQuery",
            return_value=query_mock,
        ):
            pagination = PaginationParams(limit=2, offset=0)
            result = await get_all_api_data(pagination, mock_repository)

            assert len(result.items) == 2
            assert result.total == 10
            assert result.limit == 2
            assert result.offset == 0
