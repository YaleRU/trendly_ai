import asyncio
import logging

from pyrogram import Client

from src.db import SessionLocal
from src.utils.digest_sender import send_digest_to_all_users

# from src.fetchers import check_all_sources

logger = logging.getLogger(__name__)


async def scheduled_digest_task(bot_client: Client, _user_client: Client):
    """Задача для отправки дайджестов по расписанию"""
    while True:
        try:
            db = SessionLocal()

            # Отправляем дайджесты всем пользователям
            results = await send_digest_to_all_users(bot_client, db)

            logger.info(
                f"Распределение дайджестов: "
                f"Всего: {results['total']}, "
                f"Успешно: {results['success']}, "
                f"Без статей: {results['no_articles']}, "
                f"Ошибки: {results['failed']}"
            )

            db.close()

            # Ждем до следующей проверки (например, 2 минуты)
            await asyncio.sleep(120)

        except Exception as e:
            logger.error(f"Ошибка в задаче отправки дайджестов: {e}")
            await asyncio.sleep(120)  # Ждем 2 минут перед повторной попыткой
