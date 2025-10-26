from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy import String, DateTime, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .association_tables import user_source_association
from ..base import Base
from src.config import config
import src.utils.date as date_utils
from ..models.source import SourceType


class User(Base):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(unique=True, nullable=False)
    chat_id: Mapped[int] = mapped_column(nullable=False)
    username: Mapped[str] = mapped_column(String(100))
    first_name: Mapped[Optional[str]] = mapped_column(String(100))
    last_name: Mapped[Optional[str]] = mapped_column(String(100))
    registered_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Настройки дайджеста
    digest_interval: Mapped[int] = mapped_column(default=config.DEFAULT_SEND_DIGEST_INTERVAL_MINUTES)  # в минутах
    last_digest_time: Mapped[datetime] = mapped_column(default=date_utils.get_smallest_utc())
    next_digest_time: Mapped[datetime] = mapped_column(
        default=date_utils.get_smallest_utc() + timedelta(minutes=config.DEFAULT_SEND_DIGEST_INTERVAL_MINUTES))
    is_active: Mapped[bool] = mapped_column(default=True)

    # Связи
    sources: Mapped[List["Source"]] = relationship(
        secondary=user_source_association,
        back_populates="users",
        cascade="all, delete"
    )

    __table_args__ = (
        # Составное уникальное ограничение для type и target
        UniqueConstraint('telegram_id', 'chat_id', name='uq_telegram_user_id_chat_id'),
    )

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"

    def get_sources_by_type(self, source_type: SourceType) -> List['Source']:
        return [s for s in self.sources if s.type == source_type]
