from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from pyrogram import Client
import logging

from config import config
from src.fetchers import check_all_sources
# from utils import send_digests

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()

async def setup_scheduler(user_client: Client, app: Client):
    """Настраивает периодические задачи планировщика."""
    # Задача для проверки новых новостей
    scheduler.add_job(
        check_all_sources,
        trigger=IntervalTrigger(minutes=config.CHECK_INTERVAL_MINUTES),
        args=[user_client, app],
        id="check_news",
        replace_existing=True
    )

    # Задача для отправки дайджестов (например, раз в день в 19:00)
    # Для простоты примера оставим интервал, но лучше использовать CronTrigger
    scheduler.add_job(
        send_digests,
        trigger=IntervalTrigger(minutes=config.SEND_DIGEST_INTERVAL_MINUTES),
        args=[app],
        id="send_digests",
        replace_existing=True
    )

    scheduler.start()
    logger.info("Планировщик запущен.")

    # Возвращаем объект планировщика для возможной остановки в будущем
    return scheduler

async def send_digests(app: Client):
    """Отправляет дайджесты пользователям"""
    # Ваша реализация отправки дайджестов
    logger.info("Отправка дайджестов...")
    # Здесь должен быть код из utils.py