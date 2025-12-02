"""
Доменная сущность для данных, полученных из внешних API
"""

from datetime import datetime

from src.app.domain.entities.base import BaseEntity


class ApiDataEntity(BaseEntity):
    """Сущность данных из внешнего API"""

    source: str
    title: str
    content: str
    external_id: str | None = None
    fetched_at: datetime
