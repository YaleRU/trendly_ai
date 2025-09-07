from typing import Optional, List

from sqlalchemy import and_
from sqlalchemy.orm import Session

from .base_repository import BaseRepository
from .. import User
from ..models import Source, SourceType


class SourceRepository(BaseRepository[Source]):
    """Репозиторий для работы с пользователями"""

    def __init__(self, db: Session):
        super().__init__(Source, db)

    def get_source_by_type_and_target(self, source_type: SourceType, target: str) -> Optional[Source]:
        return self.db.query(Source).filter(Source.type == source_type, Source.target == target).first()

    def get_user_sources(self, user_id: int) -> List[Source]:
        """Получает все источники конкретного пользователя"""
        return self.db.query(Source).join(Source.users).filter(User.id == user_id).all()

    def get_user_sources_by_type(self, user_id: int, source_type: SourceType) -> List[Source]:
        """Получает источники пользователя определенного типа"""
        return self.db.query(Source).join(Source.users).filter(
            User.id == user_id,
            Source.type == source_type
        ).all()

    def get_active_sources_by_type(self, user: User | None, source_type: SourceType | None) -> List[Source]:
        """Получает все источники определенного типа, которые есть у пользователей"""
        stmt = self.db.query(Source).distinct().join(Source.users)

        if user is not None:
            stmt = stmt.filter(User.id == user.id)

        if source_type is not None:
            stmt = stmt.filter(Source.type == source_type)

        return stmt.all()

    def find_or_create_source(self, source_type: SourceType, target: str, title: Optional[str] = None) -> Source:
        """Находит или создает источник"""
        source = self.get_source_by_type_and_target(source_type, target)

        if not source:
            source = Source(
                type=source_type,
                target=target,
                title=title or target
            )
            self.db.add(source)
            self.db.commit()
            self.db.refresh(source)

        return source

    def add_source_to_user(self, user: User, source_id: int) -> bool:
        """Добавляет источник пользователю"""
        source = self.db.query(Source).filter(Source.id == source_id).first()

        if source and source not in user.sources:
            user.sources.append(source)
            self.db.commit()
            return True

        return False

    def remove_source_from_user(self, user_id: int, source_id: int) -> bool:
        """Удаляет источник у пользователя"""
        user: User | None = self.db.query(User).filter(User.id == user_id).first()
        source = self.db.query(Source).filter(Source.id == source_id).first()

        if user and source and source in user.sources:
            user.sources.remove(source)
            self.db.commit()
            return True

        return False
