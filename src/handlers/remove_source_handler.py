import logging

from pyrogram import Client
from pyrogram.types import Message

from src.commands import CommandAlias
from src.db import SessionLocal
from src.db.repositories import SourceRepository
from src.handlers.common import get_user_by_telegram_id_safe, MissingEntityError

logger = logging.getLogger(__name__)


async def validate_command_args(message: Message) -> None | tuple[int]:
    command_args = message.command

    if not command_args or len(command_args) < 2:
        await message.reply_text(f"Использование: /{CommandAlias.source_info.value} [id]")
        return None

    try:
        source_id = int(command_args[1])
        return (source_id,)
    except Exception as e:
        logger.error('Не удалось получить id источника: ' + command_args[1], e)
        return None


async def remove_source_handler(_client: Client, message: Message):
    """Показывает информацию об источнике по его URL"""
    try:
        command_args = await validate_command_args(message)

        if not command_args:
            return

        (source_id,) = command_args
        user = await get_user_by_telegram_id_safe(message, message.from_user.id)
        source_to_remove = next((source for source in user.sources if source.id == source_id), None)

        # Ищем источник в БД
        if not source_to_remove:
            await message.reply_text("Источник с таким ID не найден в вашем списке.")
            return

        SourceRepository(SessionLocal()).remove_source_from_user(user.id, source_id)

        await message.reply_text("Источник удален из вашего списка")
    except MissingEntityError:
        return
    except Exception as e:
        logger.error(f"Ошибка в команде /{CommandAlias.remove_source.value}: {e}")
        await message.reply_text("Произошла ошибка при удалении источника.")
