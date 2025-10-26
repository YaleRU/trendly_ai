from datetime import timezone, datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger
from pyrogram import Client
import logging

from config import config
from src.utils.date import get_formatted_datestr, to_local
from src.db import SessionLocal
from src.fetchers import check_all_sources

# from utils import send_digests
from src.services.digest_service import DigestService
from src.db.repositories import UserRepository

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()


async def task(user_client: Client, bot_client: Client, reschedule: bool = True):
    logger.info('Сработала регулярная таска дайджеста!')
    digest_service = DigestService(SessionLocal())
    users_telegram_ids = [u.telegram_id for u in digest_service.get_inspired_users()]
    if len(users_telegram_ids) != 0:
        await check_all_sources(user_client, bot_client, users_telegram_ids)
        await digest_service.send_digest(bot_client)

    if reschedule:
        await setup_scheduler(user_client, bot_client)


async def setup_scheduler(user_client: Client, bot_client: Client):
    db = SessionLocal()
    if DigestService(db).has_inspired_users():
        await task(user_client, bot_client, False)

    user = UserRepository(db).get_user_with_earliest_digest()
    next_task_time = user.last_digest_time

    scheduler.add_job(
        task,
        trigger=DateTrigger(run_date=next_task_time, timezone=timezone.utc),
        args=[user_client, bot_client],
        id="check_news",
        replace_existing=True
    )
    logger.info(f"Запланирована таска, время срабатывания {get_formatted_datestr(to_local(next_task_time))}")

    if not scheduler.running:
        scheduler.start()
        logger.info("Планировщик запущен!")

    # Возвращаем объект планировщика для возможной остановки в будущем
    return scheduler
