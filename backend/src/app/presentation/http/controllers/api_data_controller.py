"""
Контроллер для работы с данными из внешних API
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.application.commands.fetch_api_data import FetchApiDataCommand
from src.app.application.queries.get_api_data import GetApiDataQuery
from src.app.infrastructure.persistence.database import get_db_session
from src.app.infrastructure.persistence.repositories.api_data_repository import ApiDataRepository
from src.app.presentation.http.common.pagination import PaginationParams
from src.app.presentation.http.schemas.api_data import (
    ApiDataListResponse,
    ApiDataResponse,
    FetchApiDataRequest,
)

router = APIRouter(prefix="/api/data", tags=["API Data"])


async def get_repository(session: AsyncSession = Depends(get_db_session)) -> ApiDataRepository:
    """Получение репозитория"""
    return ApiDataRepository(session)


@router.post("/fetch", response_model=ApiDataResponse, status_code=status.HTTP_201_CREATED)
async def fetch_api_data(
    request: FetchApiDataRequest,
    repository: ApiDataRepository = Depends(get_repository),
):
    """Получение данных из внешнего API и сохранение в БД"""
    command = FetchApiDataCommand(repository)
    try:
        entity = await command.execute(request.number)
        return ApiDataResponse.model_validate(entity)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении данных: {str(e)}",
        )


@router.get("/{data_id}", response_model=ApiDataResponse)
async def get_api_data_by_id(
    data_id: UUID,
    repository: ApiDataRepository = Depends(get_repository),
):
    """Получение данных по ID"""
    query = GetApiDataQuery(repository)
    entity = await query.get_by_id(data_id)
    if not entity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Данные не найдены")
    return ApiDataResponse.model_validate(entity)


@router.get("", response_model=ApiDataListResponse)
async def get_all_api_data(
    pagination: PaginationParams = Depends(),
    repository: ApiDataRepository = Depends(get_repository),
):
    """Получение всех данных с пагинацией"""
    query = GetApiDataQuery(repository)
    items, total = await query.get_all(limit=pagination.limit, offset=pagination.offset)
    return ApiDataListResponse(
        items=[ApiDataResponse.model_validate(item) for item in items],
        total=total,
        limit=pagination.limit,
        offset=pagination.offset,
    )
