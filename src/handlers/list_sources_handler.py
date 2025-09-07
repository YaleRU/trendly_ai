import logging

from pyrogram.enums import ParseMode
from pyrogram.types import Message

from src.commands import CommandAlias
from src.db import SourceType
from src.db.repositories import UserRepository
from src.handlers.common import get_user_by_telegram_id_safe, MissingEntityError

logger = logging.getLogger(__name__)


async def list_sources_handler(_client, message: Message):
    """Показывает все источники пользователя с группировкой по типам"""
    try:
        user = await get_user_by_telegram_id_safe(message, message.from_user.id)

        if not user.sources:
            await message.reply_text(
                "📭 У вас пока нет добавленных источников.\n\n"
                "Добавьте первый источник командой /" + CommandAlias.add_source.value
            )
            return

        # Группируем источники по типу
        sources_by_type = UserRepository.get_sources_by_type(user)

        # Форматируем ответ
        response = "📚 <b>Ваши источники:</b>\n\n"

        for source_type, type_sources in sources_by_type.items():
            # Добавляем иконку для каждого типа источников
            type_icon = "🔹"
            if source_type == SourceType.Telegram:
                type_icon = "📢"
            elif source_type == SourceType.RSS:
                type_icon = "📡"
            elif source_type == SourceType.WEB:
                type_icon = "🌐"

            response += f"{type_icon} <b>{source_type.value.upper()}</b>:\n"

            for i, source in enumerate(type_sources, 1):
                # Используем заголовок, если он есть, или обрезаем URL
                display_text = source.title or source.target
                if len(display_text) > 40:
                    display_text = display_text[:37] + "..."

                response += f"   {i}. {display_text}\n"
                response += f"      ID: {source.id}, URL: {source.target}\n"

            response += "\n"

        response += ("\n💡 <b>Команды для управления:</b>\n" +
                     "/" + CommandAlias.add_source.value + " [тип] [url] - добавить новый источник\n" +
                     "/" + CommandAlias.remove_source.value + " [id] - удалить источник\n" +
                     "/" + CommandAlias.source_info.value + " [id] - информация об источнике")

        # Разбиваем сообщение на части, если оно слишком длинное
        max_length = 4096  # Максимальная длина сообщения в Telegram
        if len(response) > max_length:
            parts = []
            current_part = ""

            for line in response.split('\n'):
                if len(current_part) + len(line) + 1 > max_length:
                    parts.append(current_part)
                    current_part = line + '\n'
                else:
                    current_part += line + '\n'

            if current_part:
                parts.append(current_part)

            # Отправляем части сообщения
            for part in parts:
                await message.reply_text(part, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
        else:
            await message.reply_text(response, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    except MissingEntityError as e:
        logger.error(f"Ошибка в команде /{CommandAlias.list_sources.value}: {e}")
    except Exception as e:
        logger.error(f"Ошибка в команде /{CommandAlias.list_sources.value}: {e}")
        await message.reply_text(
            "Произошла ошибка при получении списка источников. Попробуйте позже."
        )
