import logging

from pyrogram import Client
from pyrogram.enums import ParseMode
from pyrogram.types import Message

from src.commands import CommandAlias
from src.handlers.common import get_user_by_telegram_id_safe, MissingEntityError
from src.utils import date as date_utils

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


async def source_info_handler(_client: Client, message: Message):
    """Показывает информацию об источнике по его URL"""
    try:
        command_args = await validate_command_args(message)

        if not command_args:
            return

        user = await get_user_by_telegram_id_safe(message, message.from_user.id)
        (source_id,) = command_args

        source = next((source for source in user.sources if source.id == source_id), None)

        if not source:
            await message.reply_text("Источник с таким ID не найден в вашем списке.")
            return

        def get_formated_last_check() -> str:
            if source.last_checked_time:
                local_date = date_utils.to_local(source.last_checked_time)
                return date_utils.get_formatted_datestr(local_date)
            elif source.is_updating:
                return 'Обновляется сейчас...'
            else:
                return 'Никогда'

        response = (
            f"📋 <b>Информация об источнике:</b>\n\n"
            f"<b>ID:</b> {source.id}\n"
            f"<b>Тип:</b> {source.type.value}\n"
            f"<b>URL:</b> {source.target}\n"
            f"<b>Последняя проверка:</b> {get_formated_last_check()}\n\n"
            f"<b>Всего статей:</b> {len(source.articles)}\n"
            f"<b>Последняя добавленная статья:</b> {source.last_checked_article_id or 'Ничего не добавлялось'}\n\n"
            f"Используйте /{CommandAlias.remove_source.value} {source.id} чтобы удалить этот источник."
        )

        await message.reply_text(response, parse_mode=ParseMode.HTML)

    except MissingEntityError:
        return
    except Exception as e:
        logger.error(f"Ошибка в команде /{CommandAlias.source_info.value}: {e}")
        await message.reply_text("Произошла ошибка при получении информации об источнике.")
