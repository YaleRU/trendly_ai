from datetime import datetime
from typing import Optional

from sqlalchemy import String, ForeignKey, UniqueConstraint, Index
from sqlalchemy import Text
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base


class Article(Base):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    source_id: Mapped[int] = mapped_column(
        ForeignKey("sources.id", ondelete="CASCADE"),
        nullable=False
    )
    id_in_source: Mapped[str] = mapped_column(String(200), nullable=False)
    url: Mapped[str] = mapped_column(String(500), unique=True, nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(500))
    content: Mapped[Optional[str]] = mapped_column(Text)
    summary: Mapped[Optional[str]] = mapped_column(Text)
    published_at: Mapped[datetime] = mapped_column(nullable=False)
    processed_at: Mapped[datetime] = mapped_column(server_default=func.now())

    # Связи
    source: Mapped["Source"] = relationship(
        back_populates="articles",
        foreign_keys=[source_id]
    )

    __table_args__ = (
        Index('idx_articles_url', 'url'),
        Index('idx_articles_processed', 'published_at'),
        UniqueConstraint('source_id', 'id_in_source', name='idx_articles_source_id'),
    )

    def __repr__(self):
        return f"<Article(id={self.id}, title={self.title})>"
