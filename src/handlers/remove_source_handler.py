from pyrogram import Client
from pyrogram.types import Message
from src.database import db
from src.commands import CommandAlias
import logging

logger = logging.getLogger(__name__)


async def remove_source_handler(client: Client, message: Message):
    """Показывает информацию об источнике по его URL"""
    try:
        user_id = message.from_user.id
        command_args = message.command

        if len(command_args) < 2:
            await message.reply_text(f"Использование: /{CommandAlias.remove_source.value} id")
            return

        # Ищем источник в БД
        if not db.has_user_source(user_id, command_args[1]):
            await message.reply_text("Источник с таким ID не найден в вашем списке.")
            return

        db.delete_user_source(user_id, command_args[1])

        await message.reply_text("Источник удален из вашего списка")

    except Exception as e:
        logger.error(f"Ошибка в команде /{CommandAlias.remove_source.value}: {e}")
        await message.reply_text("Произошла ошибка при удалении источника.")
