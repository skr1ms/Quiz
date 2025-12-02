"""
Базовые объявления доменных сущностей
"""

from abc import ABC
from datetime import UTC, datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class BaseEntity(BaseModel, ABC):
    """Базовый класс для всех доменных сущностей"""

    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)

    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime | None = None
