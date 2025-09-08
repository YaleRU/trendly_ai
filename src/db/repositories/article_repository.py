from typing import Optional

from sqlalchemy.orm import Session

from .base_repository import BaseRepository
from ..models import Article


class ArticleRepository(BaseRepository[Article]):
    """Репозиторий для работы с пользователями"""

    def __init__(self, db: Session):
        super().__init__(Article, db)

    def get_by_source_and_external_id(self, source_id: int, id_in_source: str) -> Optional[Article]:
        return self.db.query(Article).filter(Article.source_id == source_id,
                                             Article.id_in_source == id_in_source).first()
