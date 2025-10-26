import logging
from typing import Optional, List
import src.utils.date as datetime_util

from sqlalchemy.orm import Session

from ..db.models import Article
from ..db.repositories import ArticleRepository

logger = logging.getLogger(__name__)


class ArticleService:
    """Сервис для бизнес-логики работы со статьями"""

    def __init__(self, db: Session):
        self.db = db
        self.article_repo = ArticleRepository(db)

    def add_article_to_source(self, source_id: int, article_data: dict) -> tuple[bool, Optional[Article]]:
        """Добавляет статью к источнику и возвращает (создано, статья)."""
        # Проверяем, нет ли уже статьи с таким id_in_source для этого источника
        existing_article = self.article_repo.get_by_source_and_external_id(
            source_id, article_data['id_in_source']
        )

        if existing_article:
            # Обновляем существующую статью
            return False, self._update_existing_article(existing_article, article_data)

        now = datetime_util.get_now_utc()
        # Создаем новую статью
        new_article = Article(
            source_id=source_id,
            id_in_source=article_data.get('id_in_source'),
            url=article_data.get('url'),
            title=article_data.get('title'),
            content=article_data.get('content'),
            summary=article_data.get('summary'),
            published_at=article_data.get('published_at', now),
            processed_at=article_data.get('processed_at', now)
        )

        self.db.add(new_article)
        self.db.commit()
        self.db.refresh(new_article)

        new_article.source.last_checked_article_id = new_article.id
        new_article.source.last_checked_time = new_article.processed_at
        self.db.commit()

        return True, new_article

    def _update_existing_article(self, article: Article, article_data: dict) -> Article:
        """Обновляет существующую статью"""
        article.url = article_data.get('url', article.url)
        article.title = article_data.get('title', article.title)
        article.content = article_data.get('content', article.content)
        article.summary = article_data.get('summary', article.summary)
        article.published_at = article_data.get('published_at', article.published_at)
        article.processed_at = article_data.get('processed_at', article.processed_at)

        self.db.commit()
        self.db.refresh(article)

        return article

    def add_articles_batch(self, source_id: int, articles_data: List[dict]) -> int:
        """Добавляет несколько статей к источнику пачкой"""
        added_count = 0

        for article_data in articles_data:
            try:
                created, _ = self.add_article_to_source(source_id, article_data)
                if created:
                    added_count += 1
            except Exception as e:
                logger.error(f"Ошибка при добавлении статьи: {e}")
                continue

        return added_count
