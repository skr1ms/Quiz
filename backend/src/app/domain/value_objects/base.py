"""
Базовые объявления value objects
"""

from abc import ABC

from pydantic import BaseModel, ConfigDict


class BaseValueObject(BaseModel, ABC):
    """Базовый класс для всех value objects"""

    model_config = ConfigDict(frozen=True, from_attributes=True, arbitrary_types_allowed=True)
