"""
SQLAlchemy модель для таблицы api_data
"""

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID  # noqa: N811

from src.app.infrastructure.persistence.database import Base


def utc_now():
    """Функция для получения текущего времени в UTC"""
    return datetime.now(UTC)


class ApiDataModel(Base):
    """Модель данных из внешнего API"""

    __tablename__ = "api_data"

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    source = Column(String(255), nullable=False)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    external_id = Column(String(255), nullable=True)
    fetched_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at = Column(DateTime(timezone=True), nullable=True, onupdate=utc_now)
