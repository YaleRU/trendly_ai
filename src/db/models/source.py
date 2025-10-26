from datetime import datetime
from enum import Enum
from typing import List, Optional

from sqlalchemy import String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .association_tables import user_source_association
from ..base import Base


class SourceType(Enum):
    Telegram = "telegram"
    RSS = "rss"
    WEB = "web"


class Source(Base):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    type: Mapped[SourceType]
    target: Mapped[str] = mapped_column(String(500), nullable=False)  # URL или идентификатор
    title: Mapped[Optional[str]] = mapped_column(String(200))

    # Статус и время проверок
    is_updating: Mapped[bool] = mapped_column(default=False)
    last_checked_time: Mapped[Optional[datetime]]
    last_checked_article_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("articles.id", ondelete="SET NULL")
    )

    # Связи
    users: Mapped[List["User"]] = relationship(
        secondary=user_source_association,
        back_populates="sources",
        cascade="all, delete"
    )

    articles: Mapped[List["Article"]] = relationship(
        back_populates="source",
        cascade="all, delete-orphan",
        foreign_keys="[Article.source_id]"
    )

    last_checked_article: Mapped[Optional["Article"]] = relationship(
        foreign_keys=[last_checked_article_id]
    )

    __table_args__ = (
        # Составное уникальное ограничение для type и target
        UniqueConstraint('type', 'target', name='uq_source_type_target'),
    )

    def __repr__(self):
        return f"<Source(id={self.id}, type={self.type}, target={self.target})>"
