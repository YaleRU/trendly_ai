from __future__ import annotations

import asyncio
import logging
from datetime import timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from pyrogram import Client

from config import config
from src.db import SessionLocal
from src.db.models import User
from src.fetchers import check_all_sources
from src.utils.digest_sender import send_digest_to_all_users

logger = logging.getLogger(__name__)


async def _job_fetch_sources(user_client: Client, bot_client: Client):
    db = SessionLocal()
    try:
        users = db.query(User).filter(User.is_active == True).all()  # noqa: E712
        user_ids = [u.telegram_id for u in users]
    finally:
        db.close()
    try:
        await check_all_sources(user_client, bot_client, user_ids)
        logger.info("Сработала регулярная таска источников.")
    except Exception as e:
        logger.exception("Ошибка в таске источников: %s", e)


async def _job_send_digests(bot_client: Client):
    db = SessionLocal()
    try:
        res = await send_digest_to_all_users(bot_client, db)
        logger.info("Сработала регулярная таска дайджеста: %s", res)
    except Exception as e:
        logger.exception("Ошибка в таске дайджеста: %s", e)
    finally:
        db.close()


async def setup_scheduler(user_client: Client, bot_client: Client) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone=timezone.utc)

    # Проверка источников
    scheduler.add_job(
        _job_fetch_sources,
        trigger=IntervalTrigger(minutes=config.CHECK_NEWS_INTERVAL_MINUTES),
        args=[user_client, bot_client],
        id="check_sources_interval",
        replace_existing=True,
        coalesce=True,
        max_instances=1,
    )

    # Отправка дайджестов
    scheduler.add_job(
        _job_send_digests,
        trigger=IntervalTrigger(minutes=1),
        args=[bot_client],
        id="send_digests_interval",
        replace_existing=True,
        coalesce=True,
        max_instances=1,
    )

    if not scheduler.running:
        scheduler.start()
        logger.info("Планировщик запущен!")

    # Возвращаем объект планировщика для возможной остановки в будущем
    return scheduler
