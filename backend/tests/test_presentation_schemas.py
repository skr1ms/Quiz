"""
Тесты для Pydantic схем
"""

from datetime import UTC, datetime
from uuid import uuid4

from src.app.presentation.http.schemas.api_data import (
    ApiDataListResponse,
    ApiDataResponse,
    FetchApiDataRequest,
)


class TestApiDataSchemas:
    """Тесты для схем данных API"""

    def test_fetch_api_data_request_with_number(self):
        """Тест схемы запроса с указанным числом"""
        request = FetchApiDataRequest(number=42)

        assert request.number == 42

    def test_fetch_api_data_request_without_number(self):
        """Тест схемы запроса без указанного числа"""
        request = FetchApiDataRequest()

        assert request.number is None

    def test_api_data_response_from_dict(self):
        """Тест создания схемы ответа из словаря"""
        data_id = uuid4()
        fetched_at = datetime.now(UTC)
        created_at = datetime.now(UTC)

        data = {
            "id": data_id,
            "source": "test_source",
            "title": "Test Title",
            "content": "Test Content",
            "external_id": "123",
            "fetched_at": fetched_at,
            "created_at": created_at,
            "updated_at": None,
        }

        response = ApiDataResponse(**data)

        assert response.id == data_id
        assert response.source == "test_source"
        assert response.title == "Test Title"
        assert response.content == "Test Content"
        assert response.external_id == "123"
        assert response.fetched_at == fetched_at
        assert response.created_at == created_at
        assert response.updated_at is None

    def test_api_data_list_response(self):
        """Тест схемы списка данных"""
        items = [
            ApiDataResponse(
                id=uuid4(),
                source="test_source",
                title="Test Title 1",
                content="Test Content 1",
                external_id="1",
                fetched_at=datetime.now(UTC),
                created_at=datetime.now(UTC),
                updated_at=None,
            ),
            ApiDataResponse(
                id=uuid4(),
                source="test_source",
                title="Test Title 2",
                content="Test Content 2",
                external_id="2",
                fetched_at=datetime.now(UTC),
                created_at=datetime.now(UTC),
                updated_at=None,
            ),
        ]

        response = ApiDataListResponse(items=items, total=10, limit=2, offset=0)

        assert len(response.items) == 2
        assert response.total == 10
        assert response.limit == 2
        assert response.offset == 0
