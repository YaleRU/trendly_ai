import logging
from typing import Type, TypeVar, Generic, List, Optional

from sqlalchemy.orm import Session

from ..base import Base

T = TypeVar("T", bound=Base)
logger = logging.getLogger(__name__)


class BaseRepository(Generic[T]):
    """Базовый класс репозитория с общими CRUD операциями"""

    def __init__(self, model: Type[T], db: Session):
        self.model = model
        self.db = db

    def get(self, id: int) -> Optional[T]:
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        return self.db.query(self.model).offset(skip).limit(limit).all()

    def create(self, obj: T) -> T:
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        logger.info(f"{self.model.__name__} created!")
        return obj

    def update(self, obj: T) -> T:
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, id: int) -> bool:
        obj = self.get(id)
        if obj:
            self.db.delete(obj)
            self.db.commit()
            return True
        return False

    def filter_by(self, **filters) -> List[T]:
        return self.db.query(self.model).filter_by(**filters).all()

    def first(self, **filters) -> Optional[T]:
        return self.db.query(self.model).filter_by(**filters).first()
