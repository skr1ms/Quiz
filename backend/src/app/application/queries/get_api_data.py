"""
Запросы для получения данных из БД
"""

from typing import Protocol
from uuid import UUID

from src.app.domain.entities.api_data import ApiDataEntity


class ApiDataRepositoryProtocol(Protocol):
    """Протокол репозитория для данных API"""

    async def get_by_id(self, data_id: UUID) -> ApiDataEntity | None: ...

    async def get_all(self, limit: int, offset: int) -> list[ApiDataEntity]: ...

    async def get_by_source(self, source: str, limit: int, offset: int) -> list[ApiDataEntity]: ...

    async def count(self) -> int: ...


class GetApiDataQuery:
    """Запрос для получения данных из БД"""

    def __init__(self, repository: ApiDataRepositoryProtocol):
        self.repository = repository

    async def get_by_id(self, data_id: UUID) -> ApiDataEntity | None:
        """Получение данных по ID"""
        return await self.repository.get_by_id(data_id)

    async def get_all(self, limit: int = 10, offset: int = 0) -> tuple[list[ApiDataEntity], int]:
        """Получение всех данных с пагинацией"""
        items = await self.repository.get_all(limit=limit, offset=offset)
        total = await self.repository.count()
        return items, total

    async def get_by_source(
        self, source: str, limit: int = 10, offset: int = 0
    ) -> list[ApiDataEntity]:
        """Получение данных по источнику"""
        return await self.repository.get_by_source(source, limit=limit, offset=offset)
