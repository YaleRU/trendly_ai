import logging
from pyrogram import Client
from pyrogram.types import Message
from pyrogram.errors import ChannelInvalid, ChannelPrivate, UsernameNotOccupied

from src.utils import date as date_utils
from src.config import config
from src.db import SessionLocal, SourceType
from src.db.repositories import SourceRepository, UserRepository
from src.services.source_service import SourceService

logger = logging.getLogger(__name__)


async def check_telegram_sources(user_client: Client, _bot: Client, user_telegram_id: int):
    """Проверяет Telegram-каналы на наличие новых сообщений"""
    user = UserRepository(SessionLocal()).get_by_telegram_id(user_telegram_id)

    if not user:
        logger.warning("Не найден пользователь!")

    source_service = SourceService(SessionLocal())
    user_active_sources = SourceRepository(SessionLocal()).get_active_sources_by_type(user, SourceType.Telegram)

    if not user_active_sources:
        return

    for source in user_active_sources:

        # Пропускаем источники, которые уже в процессе обновления
        if source.is_updating:
            continue

        with source_service.update_context(source):
            return
            try:
                # Получаем entity (канал/чат)
                entity = await user_client.get_chat(source.target)

                # Определяем время последней проверки(ОНА УЖЕ В UTC!) и статью
                is_first_loading = source.last_checked_time is None
                last_checked_time = date_utils.get_smallest_utc() if is_first_loading else date_utils.as_utc(
                    source.last_checked_time
                )

                logger.info(
                    f"last_checked_time of {source.target}: {date_utils.get_formatted_datestr(last_checked_time)}")

                messages = []
                async for message in user_client.get_chat_history(
                        entity.id,
                        limit=config.ARTICLES_FOR_FIRST_LOADING if is_first_loading else None
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
                        'source_id': source.id,
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
                        db.update_source_last_checked(source.id, added_article_id, message_date)

                db.update_source_last_checked(source.id, last_checked_time=date_utils.get_now_utc())

                logger.info(f"Найдено {new_articles_count} новых сообщений в канале {entity.title}")
            except Exception as e:
                # Если ошибка связана с правами доступа
                if isinstance(e, (ChannelInvalid, ChannelPrivate, UsernameNotOccupied)) or "FORBIDDEN" in str(
                        e) or "права" in str(e).lower():
                    await notify_user_about_forbidden_chanel(source.target, e)
                else:
                    logger.error(f"Ошибка при проверке Telegram-канала {source.target}: {e}")


async def notify_user_about_forbidden_chanel(target, e):
    logger.warning(f"Не удалось получить доступ к каналу с id={target}.\n"
                   f"Убедитесь, что бот имеет права на чтение этого канала.\n", e)
