from datetime import timedelta
import logging
from typing import List

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from pyrogram import Client

from src.config import config
from src.db import SessionLocal
from src.db.models import User
from src.fetchers import check_all_sources
from src.services.digest_service import DigestService

logger = logging.getLogger(__name__)


class Scheduler:
    def __init__(self, bot: Client, user_client: Client):
        self.bot = bot
        self.user_client = user_client
        self.scheduler = AsyncIOScheduler(timezone="UTC")  # работаем в UTC

    def _get_active_user_ids(self) -> List[int]:
        db = SessionLocal()
        try:
            users = db.query(User).filter(User.is_active == True).all()  # noqa: E712
            return [u.id for u in users]
        finally:
            db.close()

    async def _tick_check_sources(self):
        user_ids = self._get_active_user_ids()
        try:
            await check_all_sources(self.user_client, self.bot, user_ids)
        except Exception as e:
            logger.exception("check_all_sources failed: %s", e)

    async def _tick_send_digests(self):
        db = SessionLocal()
        try:
            service = DigestService(db)
            await service.send_digest(self.bot)
        except Exception as e:
            logger.exception("send_digest tick failed: %s", e)
        finally:
            db.close()

    def start(self):

        # проверка источников с заданным интервалом
        self.scheduler.add_job(
            self._tick_check_sources,
            trigger=IntervalTrigger(seconds=config.CHECK_NEWS_INTERVAL_SECONDS),
            id="check_news",
            replace_existing=True,
            coalesce=True,
            max_instances=1,
        )
        # отправка дайджестов раз в минуту
        self.scheduler.add_job(
            self._tick_send_digests,
            trigger=IntervalTrigger(seconds=config.SEND_NEWS_INTERVAL_SECONDS),
            id="send_digests",
            replace_existing=True,
            coalesce=True,
            max_instances=1,
        )
        self.scheduler.start()
        logger.info("Планировщик запущен: check_news=%s сек, send_digests=%s сек",
                    config.CHECK_NEWS_INTERVAL_SECONDS, config.SEND_NEWS_INTERVAL_SECONDS)


async def setup_scheduler(bot: Client, user_client: Client):
    """Back-compat wrapper. Creates and starts Scheduler. Returns the APScheduler instance."""
    sch = Scheduler(bot, user_client)
    sch.start()
    return None
