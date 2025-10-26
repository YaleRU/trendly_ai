from pyrogram import Client
import logging

from .telegram_fetcher import check_telegram_sources

logger = logging.getLogger(__name__)


async def check_all_sources(user_client: Client, bot: Client, user_telegram_ids: list[int]):
    """Главная функция, запускающая проверку всех источников."""
    logger.info("Checking all sources...")

    await check_telegram_sources(user_client, bot, user_telegram_ids)
