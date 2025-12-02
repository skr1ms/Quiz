"""
Репозиторий для работы с данными из внешних API
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.domain.entities.api_data import ApiDataEntity
from src.app.infrastructure.persistence.models.api_data import ApiDataModel


class ApiDataRepository:
    """Репозиторий для работы с api_data"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, entity: ApiDataEntity) -> ApiDataEntity:
        """Создание новой записи"""
        model = ApiDataModel(
            source=entity.source,
            title=entity.title,
            content=entity.content,
            external_id=entity.external_id,
            fetched_at=entity.fetched_at,
        )
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        entity.id = model.id
        return entity

    async def get_by_id(self, data_id: UUID) -> ApiDataEntity | None:
        """Получение записи по ID"""
        result = await self.session.execute(select(ApiDataModel).where(ApiDataModel.id == data_id))
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_entity(model)

    async def get_all(self, limit: int = 10, offset: int = 0) -> list[ApiDataEntity]:
        """Получение всех записей с пагинацией"""
        result = await self.session.execute(
            select(ApiDataModel)
            .order_by(ApiDataModel.fetched_at.desc())
            .limit(limit)
            .offset(offset)
        )
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def get_by_source(
        self, source: str, limit: int = 10, offset: int = 0
    ) -> list[ApiDataEntity]:
        """Получение записей по источнику"""
        result = await self.session.execute(
            select(ApiDataModel)
            .where(ApiDataModel.source == source)
            .order_by(ApiDataModel.fetched_at.desc())
            .limit(limit)
            .offset(offset)
        )
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def count(self) -> int:
        """Подсчет общего количества записей"""
        from sqlalchemy import func

        result = await self.session.execute(select(func.count(ApiDataModel.id)))
        return result.scalar_one()

    def _to_entity(self, model: ApiDataModel) -> ApiDataEntity:
        """Преобразование модели в сущность"""
        return ApiDataEntity(
            id=model.id,
            source=model.source,
            title=model.title,
            content=model.content,
            external_id=model.external_id,
            fetched_at=model.fetched_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
