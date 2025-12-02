"""
Pydantic схемы для HTTP представления данных API
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ApiDataResponse(BaseModel):
    """Схема ответа с данными API"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    source: str
    title: str
    content: str
    external_id: str | None
    fetched_at: datetime
    created_at: datetime
    updated_at: datetime | None


class ApiDataListResponse(BaseModel):
    """Схема ответа со списком данных API"""

    items: list[ApiDataResponse]
    total: int
    limit: int
    offset: int


class FetchApiDataRequest(BaseModel):
    """Схема запроса на получение данных из внешнего API"""

    number: int | None = None
