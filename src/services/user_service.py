from datetime import timedelta
from typing import Optional

from sqlalchemy.orm import Session

import src.utils.date as datetime_util
from ..db.models import User
from ..db.repositories import UserRepository


class UserService:
    """Сервис для бизнес-логики пользователей"""

    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)

    def get_or_create_user(self, telegram_id: int, username: str, first_name: str, last_name: str) -> User:
        """Получает или создает пользователя"""
        user = self.user_repo.get_by_telegram_id(telegram_id)

        if not user:
            user = User(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                registered_at=datetime_util.get_now_utc()
            )
            self.user_repo.create(user)

        return user

    def update_digest_interval(self, user_id: int, interval_minutes: int) -> Optional[User]:
        """Обновляет интервал отправки дайджеста"""
        user = self.user_repo.get(user_id)

        if user:
            user.digest_interval = interval_minutes
            user.next_digest_time = datetime_util.get_now_utc() + timedelta(minutes=interval_minutes)
            self.user_repo.update(user)

        return user

    def get_users_for_digest(self) -> list[User]:
        """Получает пользователей, которым нужно отправить дайджест"""
        return self.user_repo.get_users_for_digest()
