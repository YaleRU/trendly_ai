import logging
from datetime import datetime, timedelta
from pyrogram import Client
from pyrogram.types import Message
from pyrogram.errors import ChannelInvalid, ChannelPrivate, UsernameNotOccupied

from src.database import db, SourceType
from src.utils import date as date_utils

logger = logging.getLogger(__name__)


def get_default_last_checked() -> datetime:
    return date_utils.now_utc() - timedelta(hours=24)


async def check_telegram_sources(user_client: Client, bot: Client):
    """Проверяет Telegram-каналы на наличие новых сообщений"""
    user_sources = db.get_active_sources(SourceType.Telegram)

    if not user_sources:
        return

    async def notify_user_about_forbidden_chanel(target, e):
        logger.warning(f"Не удалось получить доступ к каналу с id={target}.\n"
                       f"Убедитесь, что бот имеет права на чтение этого канала.\n", e)

    for source in user_sources:

        # Пропускаем источники, которые уже в процессе обновления
        if source['is_updating'] != 0:
            continue

        source_id = source['id']
        source_target = source['target']
        db.start_source_updating(source_id)

        try:
            # Получаем entity (канал/чат)
            entity = await user_client.get_chat(source_target)

            # Определяем время последней проверки и статью

            # Преобразуем строку из БД в объект datetime
            # ОНА УЖЕ В UTC!
            last_checked_time = date_utils.as_utc(date_utils.get_dt_from_datestr(source['last_checked_time'])) if \
                source['last_checked_time'] else get_default_last_checked()

            logger.info(
                f"last_checked_time of {source_target}: {date_utils.get_formatted_datestr(last_checked_time)}")

            messages = []
            async for message in user_client.get_chat_history(
                    entity.id
            ):
                if date_utils.to_utc(message.date) > last_checked_time:
                    if isinstance(message, Message) and message.text and not message.service:
                        messages.append(message)
                    else:
                        continue
                else:
                    break

            new_articles_count = 0
            messages = reversed(messages)

            for message in messages:

                # Формируем URL к сообщению
                if entity.username:
                    message_url = f"https://t.me/{entity.username}/{message.id}"
                else:
                    message_url = f"tg://openmessage?chat_id={entity.id}&message_id={message.id}"

                message_date = date_utils.to_utc(message.date)
                article_data = {
                    'source_id': source_id,
                    'id_in_source': str(message.id),
                    'url': message_url,
                    'title': message.text[:100] + "..." if len(message.text) > 100 else message.text,
                    'content': message.text,
                    'published_at': message_date,
                }

                # Сохраняем статью и обновляем время проверки
                added_article_id = db.add_article(article_data)
                if added_article_id is not None:
                    new_articles_count += 1
                    db.update_source_last_checked(source_id, added_article_id, message_date)

            db.update_source_last_checked(source_id, last_checked_time=date_utils.now_utc())

            logger.info(f"Найдено {new_articles_count} новых сообщений в канале {entity.title}")
            db.stop_source_updating(source_id)
        except Exception as e:
            # Если ошибка связана с правами доступа
            if isinstance(e, (ChannelInvalid, ChannelPrivate, UsernameNotOccupied)) or "FORBIDDEN" in str(
                    e) or "права" in str(e).lower():
                await notify_user_about_forbidden_chanel(source_target, e)
            else:
                logger.error(f"Ошибка при проверке Telegram-канала {source_target}: {e}")

            db.stop_source_updating(source_id)
