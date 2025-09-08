from typing import List, Optional, Dict

from sqlalchemy import and_
from sqlalchemy.orm import Session

from .base_repository import BaseRepository
from .source_repository import SourceRepository
from .. import SourceType
from ..models import User


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

    def get_users_for_digest(self) -> List[User]:
        from sqlalchemy import or_
        from datetime import datetime

        now = datetime.now()
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
