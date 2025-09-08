from datetime import datetime
import logging
from contextlib import contextmanager
import src.utils.date as datetime_util
from typing import List, Optional
from sqlalchemy.orm import Session
from ..db.repositories import SourceRepository, UserRepository
from ..db.models import Source, SourceType, User

logger = logging.getLogger(__name__)


class SourceExistsError(Exception):
    def __init__(self, source_url: str):
        super().__init__(f"Источник с таким url уже существует: {source_url}")


class SourceService:
    """Сервис для бизнес-логики работы с источниками"""

    def __init__(self, db: Session):
        self.source_repo = SourceRepository(db)
        self.db = db

    def get_user_sources(self, user_id: int) -> List[Source]:
        """Получает все источники пользователя"""
        return self.source_repo.get_user_sources(user_id)

    def get_user_telegram_sources(self, user_id: int) -> List[Source]:
        """Получает Telegram-источники пользователя"""
        return self.source_repo.get_user_sources_by_type(user_id, SourceType.Telegram)

    def get_user_rss_sources(self, user_id: int) -> List[Source]:
        """Получает RSS-источники пользователя"""
        return self.source_repo.get_user_sources_by_type(user_id, SourceType.RSS)

    def get_user_web_sources(self, user_id: int) -> List[Source]:
        """Получает веб-источники пользователя"""
        return self.source_repo.get_user_sources_by_type(user_id, SourceType.WEB)

    def add_source_to_user(self, user: User, source_type: SourceType, target: str,
                           title: Optional[str] = None) -> Source:
        """Добавляет источник пользователю"""
        # Находим или создаем источник
        source = self.source_repo.find_or_create_source(source_type, target, title)

        # Добавляем источник пользователю
        self.source_repo.add_source_to_user(user, source.id)

        return source

    def add_source_to_user_by_telegram_user_id(self, telegram_user_id: int, source_type: SourceType, target: str,
                                               title: Optional[str] = None) -> Source:
        """Добавляет источник пользователю"""
        # Находим или создаем источник
        source = self.source_repo.find_or_create_source(source_type, target, title)

        user = UserRepository(self.db).get_by_telegram_id(telegram_user_id)

        if not user:
            raise Exception(f'User with telegram id="{telegram_user_id}" was not found!')

        if user in source.users:
            raise SourceExistsError(source_url=source.target)

        # Добавляем источник пользователю
        self.source_repo.add_source_to_user(user, source.id)

        return source

    def remove_source_from_user(self, user_id: int, source_id: int) -> bool:
        """Удаляет источник у пользователя"""
        return self.source_repo.remove_source_from_user(user_id, source_id)

    def start_update(self, source: Source) -> bool:
        """Начинает обновление источника"""
        if source.is_updating:
            logger.warning(f"Источник {source.id} уже обновляется")
            return False

        source.is_updating = True
        self.db.commit()
        logger.info(f"Начато обновление источника {source.id}")
        return True

    def stop_update(self, source: Source, success: bool = True) -> bool:
        """Завершает обновление источника"""
        if not source.is_updating:
            logger.warning(f"Источник {source.id} не обновлялся")
            return False

        source.is_updating = False
        source.last_checked_time = datetime_util.get_now_utc()
        self.db.commit()

        status = "успешно" if success else "с ошибкой"
        logger.info(f"Завершено обновление источника {source.id} {status}")
        return True

    def get_stuck_sources(self) -> List[Source]:
        """Получает источники, которые зависли в состоянии обновления"""
        return self.db.query(Source).filter(Source.is_updating == True).all()

    def force_stop_all_updates(self) -> int:
        """Принудительно останавливает все обновления (при перезапуске)"""
        stuck_sources = self.get_stuck_sources()

        for source in stuck_sources:
            source.is_updating = False
            logger.warning(f"Принудительно остановлено обновление источника {source.id}")

        self.db.commit()
        return len(stuck_sources)

    @contextmanager
    def update_context(self, source: Source):
        """Контекстный менеджер для обновления источника"""
        if not self.start_update(source):
            yield None
            return

        try:
            yield source
            self.stop_update(source, success=True)

        except Exception as e:
            self.stop_update(source, success=False)
            logger.error(f"Ошибка в контексте обновления источника {source.id}: {e}")
            raise

    def update_last_checked(self, source: Source, last_checked_time: datetime,
                            last_checked_article_id: None | int = None):

        source.last_checked_time = last_checked_time

        if last_checked_article_id:
            source.last_checked_article_id = last_checked_article_id

        self.db.commit()
