"""
Тесты для инфраструктурных адаптеров
"""

from unittest.mock import MagicMock, patch

import httpx
import pytest

from src.app.infrastructure.adapters.public_api_client import PublicApiClient


class TestPublicApiClient:
    """Тесты для клиента публичного API"""

    @pytest.mark.asyncio
    async def test_get_number_fact_success(self):
        """Тест успешного получения вопроса викторины"""
        client = PublicApiClient()
        mock_response_data = [
            {
                "question": "What is the answer to life, the universe, and everything?",
                "answer": "42",
                "category": "Science",
            }
        ]

        with patch("httpx.AsyncClient.get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            result = await client.get_number_fact(42)

            assert result["source"] == "apininjas"
            assert result["title"] == "Вопрос викторины (число 42)"
            assert "What is the answer" in result["content"]
            assert "42" in result["content"]
            assert result["external_id"] == "42"

    @pytest.mark.asyncio
    async def test_get_random_fact_success(self):
        """Тест успешного получения случайного вопроса викторины"""
        client = PublicApiClient()
        mock_response_data = [
            {
                "question": "What is considered a lucky number?",
                "answer": "7",
                "category": "",
            }
        ]

        with patch("httpx.AsyncClient.get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            result = await client.get_random_fact()

            assert result["source"] == "apininjas"
            assert result["title"] == "Случайный вопрос викторины"
            assert "What is considered" in result["content"]
            assert "7" in result["content"]
            assert result["external_id"] is None

    @pytest.mark.asyncio
    async def test_get_number_fact_http_error(self):
        """Тест обработки HTTP ошибки"""
        client = PublicApiClient()

        with patch("httpx.AsyncClient.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.text = "Internal Server Error"
            mock_response.json.return_value = {"error": "Server error"}
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Error", request=MagicMock(), response=mock_response
            )
            mock_get.return_value = mock_response

            with pytest.raises(ValueError, match="API вернул ошибку"):
                await client.get_number_fact(42)
