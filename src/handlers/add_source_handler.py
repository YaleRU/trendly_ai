import logging

from pyrogram import Client
from pyrogram.errors import ChannelInvalid, ChannelPrivate, UsernameNotOccupied
from pyrogram.types import Message

from src.commands import CommandAlias
from src.db import SessionLocal, SourceType
from src.services.source_service import SourceService, SourceExistsError

logger = logging.getLogger(__name__)


async def add_source_handler(user_client: Client, message: Message):
    """Обрабатывает команду /add_source."""

    command_args = await validate_command_args(message)

    if not command_args:
        return

    (source_type, input_url) = command_args

    if source_type == SourceType.Telegram:
        source_info = await get_telegram_source_info(user_client, message, input_url)
    else:
        # TODO Реализовать валидацию других типов источников здесь
        source_info = (input_url, '')

    if not source_info:
        return

    (source_url, source_title) = source_info

    try:
        source_service = SourceService(SessionLocal())
        source_service.add_source_to_user_by_telegram_user_id(message.from_user.id, source_type, source_url,
                                                              source_title)
        await message.reply_text(f"Источник {input_url} ({source_type.value}) успешно добавлен!")
    except SourceExistsError:
        await message.reply_text(
            "❌ Этот источник уже добавлен в ваш список.\n"
            f"Используйте /{CommandAlias.list_sources.value} чтобы просмотреть все ваши источники."
        )
    except Exception as e:
        logger.error(f"Произошла ошибка при добавлении источника {input_url}: {e}")
        await message.reply_text("Произошла ошибка при добавлении источника.")


async def validate_command_args(message: Message) -> None | tuple[SourceType, str]:
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
        return None

    source_type = SourceType(command_args[1].lower())

    if source_type is None:
        await message.reply_text(f"Тип должен быть один из: {', '.join([member.value for member in SourceType])}")
        return None

    return source_type, command_args[2]


async def get_telegram_source_info(user_client: Client, message: Message, input_url: str) -> None | tuple[
    str, str]:
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

    entity_id = _extract_entity_identifier(input_url)

    if entity_id is None:
        await message.reply_text(f"Неверный формат URL для Telegram источника: {input_url}!")
        return None

    try:
        entity = await user_client.get_chat(entity_id)

        if entity is None:
            await message.reply_text(f"Неверный формат URL для Telegram источника: {input_url}!")
            return None

        return str(entity_id), entity.title
    except (ChannelInvalid, ChannelPrivate, UsernameNotOccupied) as e:
        logger.warning(f"Не удалось получить доступ к каналу {input_url}: {e}")
        await message.reply_text(
            f"Произошла ошибка при добавлении источника.\nНе удалось получить доступ к каналу {input_url}!")
        return None
    except Exception as e:
        logger.warning(f"Произошла ошибка при добавлении источника {input_url}: {e}")
        await message.reply_text(
            "Произошла ошибка при добавлении источника.\n" + \
            f"Возможно, неверный формат URL для Telegram источника: {input_url}!")
        return None
