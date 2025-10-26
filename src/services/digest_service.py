from __future__ import annotations

import logging
from collections import defaultdict
from datetime import timedelta
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from src.db.models import User, Article, Source, user_source_association
from src.summarizer import summarize_text
import src.utils.date as date_utils

logger = logging.getLogger(__name__)


class DigestService:
    """Сервис для генерации дайджестов новостей"""

    def __init__(self, db: Session):
        self.db = db

    # Совместимость со старым кодом
    def has_inspired_users(self) -> bool:
        return len(self.get_active_users_due()) > 0

    def get_active_users_due(self) -> List[User]:
        now = date_utils.get_now_utc()
        return (
            self.db.query(User)
            .filter(User.is_active == True)  # noqa: E712
            .filter(User.next_digest_time <= now)
            .all()
        )

    def mark_digest_sent(self, user: User) -> None:
        now = date_utils.get_now_utc()
        user.last_digest_time = now
        try:
            interval_min = int(getattr(user, "digest_interval", 60))
        except Exception:
            interval_min = 60
        user.next_digest_time = now + timedelta(minutes=interval_min)
        self.db.commit()

    # --- Articles ---
    def get_user_articles(self, user_id: int, hours: int = 24) -> List[Article]:
        """Статьи пользователя за указанное окно."""
        since = date_utils.get_now_utc() - timedelta(hours=hours)
        q = (
            self.db.query(Article)
            .join(Source, Source.id == Article.source_id)
            .join(user_source_association, user_source_association.c.source_id == Source.id)
            .join(User, User.id == user_source_association.c.user_id)
            .filter(User.id == user_id)
            .filter(Article.published_at >= since)
            .filter(Article.title.isnot(None))
            .order_by(Article.published_at.desc())
        )
        return q.all()

    async def ensure_summaries(self, articles: List[Article]) -> None:
        """Сгенерировать summary там, где пусто. Тихий фейл на ошибках."""
        changed = False
        for a in articles:
            if not a.summary and (a.content or a.title):
                try:
                    text = a.content or a.title or ""
                    a.summary = await summarize_text(text)
                    changed = True
                except Exception as e:
                    logger.warning("summarize failed for article id=%s: %s", getattr(a, "id", None), e)
        if changed:
            self.db.commit()

    def group_by_source(self, articles: List[Article]) -> Dict[Source, List[Article]]:
        grouped: Dict[Source, List[Article]] = defaultdict(list)
        for a in articles:
            # Ensure relationship is loaded. In case not, fetch Source by id.
            src = getattr(a, "source", None)
            if src is None:
                src = self.db.query(Source).get(a.source_id)  # type: ignore[call-arg]
            grouped[src].append(a)  # type: ignore[index]
        return dict(grouped)

    async def generate_digest(self, user_id: int, hours: int = 24, per_source_limit: int = 8) -> Optional[str]:
        """Возвращает готовый HTML дайджест или None, если статей нет."""
        articles = self.get_user_articles(user_id, hours)
        if not articles:
            return None
        await self.ensure_summaries(articles)

        grouped = self.group_by_source(articles)

        parts: List[str] = [f"📰 <b>Ваш дайджест за {hours}ч</b>"]
        for source, items in grouped.items():
            title = source.title or source.target  # type: ignore[attr-defined]
            parts.append(f"<b>{title}</b>")
            for a in items[:per_source_limit]:
                t = (a.title or "Без заголовка").strip()
                s = (a.summary or a.content or "").strip()
                if len(s) > 260:
                    s = s[:260] + "…"
                url = a.url or ""
                parts.append(f"• <b>{t}</b>\n{s}\n{url}")
            extra = max(0, len(items) - per_source_limit)
            if extra:
                parts.append(f"…и ещё {extra}")

        msg = "\n\n".join(parts)
        return (msg[:4000] + "…") if len(msg) > 4000 else msg

    # Совместимость со старым кодом
    def get_inspired_users(self):
        return self.get_active_users_due()
