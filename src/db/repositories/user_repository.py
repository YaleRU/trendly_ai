from typing import List, Optional, Dict

from sqlalchemy import and_
from sqlalchemy.orm import Session

from .base_repository import BaseRepository
from .source_repository import SourceRepository
from .. import SourceType
from ..models import User
import src.utils.date as datetime_util
from sqlalchemy import func, case, or_
from datetime import datetime, timedelta


class UserRepository(BaseRepository[User]):
    """Репозиторий для работы с пользователями"""

    def __init__(self, db: Session):
        super().__init__(User, db)

    def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.telegram_id == telegram_id).first()

    def get_by_username(self, username: str) -> Optional[User]:
        return self.db.query(User).filter(User.username == username).first()

    def get_active_users(self) -> List[User]:
        return self.db.query(User).filter(User.is_active == True).all()

    def get_user_with_earliest_digest(self) -> Optional[User]:
        """Возвращает активного пользователя с ближайшим временем следующего дайджеста.
        Dialect-agnostic: вычисление на Python, без SQL make_interval.
        """
        users = (
            self.db.query(User)
            .filter(User.is_active == True)  # noqa: E712
            .all()
        )
        if not users:
            return None

        def next_time(u: User):
            base = u.last_digest_time or datetime_util.get_now_utc()
            try:
                mins = int(getattr(u, "digest_interval", 60) or 60)
            except Exception:
                mins = 60
            return base + timedelta(minutes=mins)

        return min(users, key=next_time)

    def get_users_for_digest(self) -> List[User]:
        from sqlalchemy import or_

        now = datetime_util.get_now_utc()
        return self.db.query(User).filter(
            and_(
                User.is_active == True,
                or_(
                    User.next_digest_time == None,
                    User.next_digest_time <= now
                )
            )
        ).all()

    @staticmethod
    def get_sources_by_type(user: User) -> Dict[SourceType, List['Source']]:
        return {
            SourceType.Telegram: SourceRepository.get_sources_by_type(
                user.sources, SourceType.Telegram
            ),
            SourceType.RSS: SourceRepository.get_sources_by_type(
                user.sources, SourceType.RSS
            ),
            SourceType.WEB: SourceRepository.get_sources_by_type(
                user.sources, SourceType.WEB
            )
        }
