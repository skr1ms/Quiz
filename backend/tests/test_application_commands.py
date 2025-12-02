"""
Тесты для команд приложения
"""

from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.app.application.commands.fetch_api_data import FetchApiDataCommand
from src.app.domain.entities.api_data import ApiDataEntity


class TestFetchApiDataCommand:
    """Тесты для команды получения данных из внешнего API"""

    @pytest.mark.asyncio
    async def test_execute_with_number(self):
        """Тест выполнения команды с указанным числом"""
        mock_repository = AsyncMock()
        mock_api_client = AsyncMock()

        mock_api_client.get_number_fact.return_value = {
            "source": "numbersapi",
            "title": "Факт о числе 42",
            "content": "42 is the answer",
            "external_id": "42",
        }

        entity_id = uuid4()
        mock_repository.create.return_value = ApiDataEntity(
            id=entity_id,
            source="numbersapi",
            title="Факт о числе 42",
            content="42 is the answer",
            external_id="42",
            fetched_at=datetime.now(UTC),
        )

        command = FetchApiDataCommand(mock_repository, mock_api_client)
        result = await command.execute(42)

        mock_api_client.get_number_fact.assert_called_once_with(42)
        mock_api_client.get_random_fact.assert_not_called()
        mock_repository.create.assert_called_once()
        assert result.source == "numbersapi"
        assert result.title == "Факт о числе 42"
        assert result.content == "42 is the answer"
        assert result.external_id == "42"

    @pytest.mark.asyncio
    async def test_execute_without_number(self):
        """Тест выполнения команды без указанного числа"""
        mock_repository = AsyncMock()
        mock_api_client = AsyncMock()

        mock_api_client.get_random_fact.return_value = {
            "source": "numbersapi",
            "title": "Факт о числе 7",
            "content": "7 is lucky",
            "external_id": "7",
        }

        entity_id = uuid4()
        mock_repository.create.return_value = ApiDataEntity(
            id=entity_id,
            source="numbersapi",
            title="Факт о числе 7",
            content="7 is lucky",
            external_id="7",
            fetched_at=datetime.now(UTC),
        )

        command = FetchApiDataCommand(mock_repository, mock_api_client)
        result = await command.execute()

        mock_api_client.get_random_fact.assert_called_once()
        mock_api_client.get_number_fact.assert_not_called()
        mock_repository.create.assert_called_once()
        assert result.source == "numbersapi"
        assert result.title == "Факт о числе 7"
        assert result.content == "7 is lucky"
        assert result.external_id == "7"

    @pytest.mark.asyncio
    async def test_execute_defaults_api_client(self):
        """Тест создания команды с дефолтным API клиентом"""
        mock_repository = AsyncMock()
        command = FetchApiDataCommand(mock_repository)

        assert command.api_client is not None
        assert command.repository == mock_repository
