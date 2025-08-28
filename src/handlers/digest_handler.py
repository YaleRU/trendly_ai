import logging

from pyrogram import filters, Client
from pyrogram.types import Message

from src.db import SessionLocal
from src.utils.digest_sender import send_digest_to_user
from .common import get_user_by_telegram_id_safe

logger = logging.getLogger(__name__)


async def digest_handler(bot_client: Client, message: Message):
    """Обработчик команды для показа дайджеста"""
    try:
        db = SessionLocal()
        user = await get_user_by_telegram_id_safe(message, message.from_user.id)

        # Отправляем дайджест
        success = await send_digest_to_user(bot_client, db, user.id, user.chat_id)

        if not success:
            await message.reply_text(
                "📭 У вас пока нет новых статей.\n\n"
                "Попробуйте позже или добавьте больше источников с помощью /add_source"
            )

    except Exception as e:
        logger.error(f"Ошибка в команде дайджеста: {e}")
        await message.reply_text("Произошла ошибка при формировании дайджеста.")

# Регистрируем обработчик
# TODO: Еще можно вот прибивать команды
# digest_filter = filters.command(["digest", "news", "дайджест"]) & filters.private
