"""
Команда для получения данных из внешнего API и сохранения в БД
"""

from datetime import UTC, datetime
from typing import Protocol

from src.app.domain.entities.api_data import ApiDataEntity
from src.app.infrastructure.adapters.public_api_client import PublicApiClient


class ApiDataRepositoryProtocol(Protocol):
    """Протокол репозитория для данных API"""

    async def create(self, entity: ApiDataEntity) -> ApiDataEntity: ...


class FetchApiDataCommand:
    """Команда для получения и сохранения данных из внешнего API"""

    def __init__(
        self, repository: ApiDataRepositoryProtocol, api_client: PublicApiClient | None = None
    ):
        self.repository = repository
        self.api_client = api_client or PublicApiClient()

    async def execute(self, number: int | None = None) -> ApiDataEntity:
        """Выполнение команды получения данных"""
        if number:
            data_dict = await self.api_client.get_number_fact(number)
        else:
            data_dict = await self.api_client.get_random_fact()

        entity = ApiDataEntity(
            source=data_dict["source"],
            title=data_dict["title"],
            content=data_dict["content"],
            external_id=data_dict.get("external_id"),
            fetched_at=datetime.now(UTC),
        )

        return await self.repository.create(entity)
