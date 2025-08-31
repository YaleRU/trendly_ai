from pyrogram import Client
from pyrogram.types import Message
from src.database import db, SourceType, SourceExistsError
from src.commands import CommandAlias
from pyrogram.errors import ChannelInvalid, ChannelPrivate, UsernameNotOccupied

import sqlite3
import logging

logger = logging.getLogger(__name__)


async def add_source_handler(user_client: Client, message: Message):
    """Обрабатывает команду /add_source."""

    command_args = message.command

    # Здесь должна быть логика парсинга аргументов и добавления источника в БД
    # Для примера: /add_source rss https://example.com/rss
    if len(command_args) < 3:
        await message.reply_text(
            "Недостаточно аргументов. Использование:\n"
            f"/{CommandAlias.add_source.value} [тип] [url]\n\n"
            f"Примеры:\n/{CommandAlias.add_source.value} {SourceType.Telegram.value} @username\n"
            f"/{CommandAlias.add_source.value} {SourceType.RSS.value} https://example.com/rss\n"
        )
        return

    user_id = message.from_user.id
    source_type = command_args[1].lower()

    # Валидация типа и URL...
    # TODO: Перейти на автогенерацию из Enum SourceType
    allowed_types = [SourceType.Telegram.value, SourceType.RSS.value, SourceType.Web.value]
    if source_type not in allowed_types:
        await message.reply_text(f"Тип должен быть один из: {', '.join(allowed_types)}")
        return

    input_url = command_args[2]

    if source_type == SourceType.Telegram.value:
        entity_id = _extract_entity_identifier(input_url)

        if entity_id is None:
            await message.reply_text(f"Неверный формат URL для Telegram источника: {input_url}!")
            return

        try:
            entity = await user_client.get_chat(entity_id)

            if entity is None:
                await message.reply_text(f"Неверный формат URL для Telegram источника: {input_url}!")
                return

            source_url = str(entity_id)
        except (ChannelInvalid, ChannelPrivate, UsernameNotOccupied) as e:
            logger.warning(f"Не удалось получить доступ к каналу {input_url}: {e}")
            await message.reply_text(
                f"Произошла ошибка при добавлении источника.\nНе удалось получить доступ к каналу {input_url}!")
            return
        except Exception as e:
            logger.warning(f"Произошла ошибка при добавлении источника {input_url}: {e}")
            await message.reply_text("Произошла ошибка при добавлении источника.")
            return

    else:
        source_url = command_args[2]

    try:
        db.add_user_source(user_id, source_type, source_url)
    except SourceExistsError:
        await message.reply_text(
            "❌ Этот источник уже добавлен в ваш список.\n"
            f"Используйте /{CommandAlias.list_sources.value} чтобы просмотреть все ваши источники."
        )
        return
    except sqlite3.Error as e:
        logger.error(f"Произошла ошибка при добавлении источника {input_url}: {e}")
        await message.reply_text("Произошла ошибка при добавлении источника.")
        return

    await message.reply_text(f"Источник {input_url} ({source_type}) успешно добавлен!")


def _extract_entity_identifier(url: str) -> str:
    """Извлекает идентификатор сущности из URL Telegram"""
    # Обрабатываем разные форматы URL
    if url.startswith('https://t.me/') or url.startswith('t.me/'):
        # https://t.me/channel_name
        return url.split('/')[-1]
    elif url.startswith('@'):
        # @channel_name
        return url[1:]
    elif url.isdigit() or (url.startswith('-') and url[1:].isdigit()):
        # ID канала (12345 или -10012345)
        return url
    else:
        # channel_name (без @)
        return url
