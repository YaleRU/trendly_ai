from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import declared_attr


class Base(DeclarativeBase):
    """Базовый класс для всех моделей"""

    metadata = MetaData()

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """Генерирует имя таблицы на основе имени класса"""
        return cls.__name__.lower() + "s"
