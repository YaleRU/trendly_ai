import logging
from typing import List, Optional

from pyrogram import Client
from pyrogram.errors import UsernameNotOccupied, ChannelPrivate, ChannelInvalid
from pyrogram.types import Message

from src.db import SessionLocal
from src.db.models import User, Source, SourceType
from src.services.article_service import ArticleService
from src.services.source_service import SourceService
from src.utils import date as date_utils

logger = logging.getLogger(__name__)


def _normalize_target(target: str) -> Optional[str]:
    if not target:
        return None
    t = target.strip()
    for pref in ("https://t.me/", "http://t.me/", "t.me/"):
        if t.startswith(pref):
            t = t[len(pref):]
            break
    if t.startswith("@"):
        t = t[1:]
    return t or None


async def _iter_recent_messages(client: Client, chat: str, limit: int = 50):
    async for msg in client.get_chat_history(chat, limit=limit):
        yield msg


async def check_telegram_sources(user_client: Client, bot: Client, user_ids: List[int]) -> None:
    """Проверяет Telegram-каналы на новые сообщения и сохраняет их в БД."""
    db = SessionLocal()
    article_service = ArticleService(db)
    source_service = SourceService(db)
    try:
        if not user_ids:
            return

        sources: List[Source] = []
        users = db.query(User).filter(User.id.in_(user_ids), User.is_active == True).all()  # noqa: E712
        for u in users:
            for s in u.sources:
                if getattr(s, "type", None) == SourceType.Telegram:
                    sources.append(s)

        if not sources:
            logger.info("Нет Telegram-источников для проверки.")
            return

        for src in sources:
            if src.is_updating:
                continue

            norm = _normalize_target(src.target or "")
            if not norm:
                logger.warning("Источник %s без target, пропуск", getattr(src, "id", None))
                continue

            new_count = 0
            try:
                with source_service.update_context(src):
                    last_id = src.last_checked_article.id_in_source if src.last_checked_article else None  # type: ignore[attr-defined]
                    last_id_int = int(last_id) if last_id and str(last_id).isdigit() else None

                    async for m in _iter_recent_messages(user_client, norm, limit=50):
                        if not isinstance(m, Message):
                            continue
                        text = m.text or m.caption or ""
                        if not text:
                            continue
                        if last_id_int is not None and m.id <= last_id_int:
                            continue

                        title = (text[:100] + "…") if len(text) > 100 else text
                        published_at = m.date
                        if published_at and published_at.tzinfo:
                            published_at = published_at.astimezone(date_utils.UTC).replace(tzinfo=None)

                        message_url = f"https://t.me/{norm}/{m.id}"

                        data = {
                            "id_in_source": str(m.id),
                            "url": message_url,
                            "title": title,
                            "content": text,
                            "summary": text,
                            "published_at": published_at or date_utils.get_now_utc(),
                            "processed_at": date_utils.get_now_utc(),
                        }

                        article = article_service.add_article_to_source(src.id, data)
                        if article:
                            new_count += 1

                    source_service.update_last_checked(src, date_utils.get_now_utc())
                if new_count:
                    logger.info("Канал %s: добавлено %d сообщений.", norm, new_count)
                else:
                    logger.info("Канал %s: новых сообщений нет.", norm)
            except UsernameNotOccupied:
                logger.warning("Канал @%s не найден.", norm)
            except (ChannelPrivate, ChannelInvalid) as e:
                logger.warning("Нет доступа к каналу @%s: %s", norm, e)
            except Exception as e:
                logger.exception("Ошибка при обработке канала @%s: %s", norm, e)
    finally:
        db.close()
