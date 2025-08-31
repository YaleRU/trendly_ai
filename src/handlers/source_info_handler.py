from pyrogram import Client
from pyrogram.types import Message
from pyrogram.enums import ParseMode
from src.database import db
from src.commands import CommandAlias
import logging

logger = logging.getLogger(__name__)


async def source_info_handler(_client: Client, message: Message):
    """Показывает информацию об источнике по его URL"""
    try:
        command_args = message.command

        if len(command_args) < 2:
            await message.reply_text(f"Использование: /{CommandAlias.source_info.value} id")
            return

        # Ищем источник в БД
        source = db.get_source(command_args[1])

        if not source:
            await message.reply_text("Источник с таким ID не найден в вашем списке.")
            return

        response = (
            f"📋 <b>Информация об источнике:</b>\n\n"
            f"<b>ID:</b> {source['id']}\n"
            f"<b>Тип:</b> {source['type']}\n"
            f"<b>URL:</b> {source['target']}\n"
            f"<b>Последняя проверка:</b> {source['last_checked_time'] or ('Обновляется сейчас...' if source['is_updating'] != 0 else 'Никогда')}\n\n"
            f"<b>Всего статей:</b> {len(db.get_articles(source['id']))}\n"
            f"<b>Последняя добавленная статья:</b> {source['last_checked_article_id'] or 'Ничего не добавлялось'}\n\n"
            f"Используйте /{CommandAlias.remove_source.value} {source['id']} чтобы удалить этот источник."
        )

        await message.reply_text(response, parse_mode=ParseMode.HTML)

    except Exception as e:
        logger.error(f"Ошибка в команде /{CommandAlias.source_info.value}: {e}")
        await message.reply_text("Произошла ошибка при получении информации об источнике.")
