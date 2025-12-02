"""
Тесты для доменных сущностей
"""

from datetime import UTC, datetime
from uuid import uuid4

from src.app.domain.entities.api_data import ApiDataEntity


class TestApiDataEntity:
    """Тесты для сущности ApiDataEntity"""

    def test_create_api_data_entity(self):
        """Тест создания сущности ApiDataEntity"""
        entity_id = uuid4()
        fetched_at = datetime.now(UTC)
        created_at = datetime.now(UTC)

        entity = ApiDataEntity(
            id=entity_id,
            source="test_source",
            title="Test Title",
            content="Test Content",
            external_id="123",
            fetched_at=fetched_at,
            created_at=created_at,
        )

        assert entity.id == entity_id
        assert entity.source == "test_source"
        assert entity.title == "Test Title"
        assert entity.content == "Test Content"
        assert entity.external_id == "123"
        assert entity.fetched_at == fetched_at
        assert entity.created_at == created_at
        assert entity.updated_at is None

    def test_create_api_data_entity_without_external_id(self):
        """Тест создания сущности без external_id"""
        entity = ApiDataEntity(
            source="test_source",
            title="Test Title",
            content="Test Content",
            fetched_at=datetime.now(UTC),
        )

        assert entity.external_id is None
        assert entity.source == "test_source"
        assert entity.title == "Test Title"
        assert entity.content == "Test Content"

    def test_api_data_entity_auto_generates_id(self):
        """Тест авто-генерации ID для сущности"""
        entity = ApiDataEntity(
            source="test_source",
            title="Test Title",
            content="Test Content",
            fetched_at=datetime.now(UTC),
        )

        assert entity.id is not None
        assert isinstance(entity.id, type(uuid4()))
