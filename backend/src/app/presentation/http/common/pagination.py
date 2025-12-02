"""
Общие HTTP утилиты для пагинации
"""

from pydantic import BaseModel, Field


class PaginationParams(BaseModel):
    """Параметры пагинации для API эндпоинтов"""

    limit: int = Field(default=10, ge=1, le=100, description="Количество элементов на странице")
    offset: int = Field(default=0, ge=0, description="Количество пропущенных элементов")


class PaginatedResponse(BaseModel):
    """Обертка для пагинированного ответа"""

    items: list
    total: int
    limit: int
    offset: int
