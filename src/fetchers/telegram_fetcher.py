import logging

from pyrogram import Client
from pyrogram.errors import UsernameNotOccupied, ChannelPrivate, ChannelInvalid
from pyrogram.types import Message

from src.config import config
from src.db import SessionLocal, SourceType
from src.db.repositories import UserRepository
from src.db.repositories.article_repository import ArticleRepository
from src.services.article_service import ArticleService
from src.services.source_service import SourceService
from src.utils import date as date_utils

logger = logging.getLogger(__name__)


async def check_telegram_sources(user_client: Client, _bot: Client, user_telegram_ids: list[int]):
    """Проверяет Telegram-каналы на наличие новых сообщений"""
    source_service = SourceService(SessionLocal())
    users_sources = source_service.get_sources_for_users(user_telegram_ids, SourceType.Telegram)

    if not users_sources:
        return

    for source in users_sources:

        # Пропускаем источники, которые уже в процессе обновления
        if source.is_updating:
            continue

        with source_service.update_context(source):
            try:
                try:
                    # Получаем entity (канал/чат)
                    entity = await user_client.get_chat(source.target)
                except Exception as e:
                    # Если ошибка связана с правами доступа
                    if isinstance(e, (ChannelInvalid, ChannelPrivate, UsernameNotOccupied)) or "FORBIDDEN" in str(
                            e) or "права" in str(e).lower():
                        await notify_user_about_forbidden_chanel(source.target, e)
                    else:
                        raise e

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

                    if ArticleRepository(SessionLocal()).get_by_source_and_external_id(source.id, message.id):
                        logger.warning(
                            f"Статья {message.text[:50]}(id={message.id}) у истоника {source.target} уже есть в БД!")
                        continue

                    # Формируем URL к сообщению
                    if entity.username:
                        message_url = f"https://t.me/{entity.username}/{message.id}"
                    else:
                        message_url = f"tg://openmessage?chat_id={entity.id}&message_id={message.id}"

                    message_date = date_utils.to_utc(message.date)

                    (added, article) = ArticleService(SessionLocal()).add_article_to_source(source.id, {
                        'id_in_source': str(message.id),
                        'url': message_url,
                        'title': message.text[:100] + "..." if len(message.text) > 100 else message.text,
                        'content': message.text,
                        'summary': message.text,
                        'published_at': message_date,
                        'processed_at': date_utils.get_now_utc(),
                    })

                    if added:
                        new_articles_count += 1
                        logger.info(f"Добавлена статья {article}")

                source_service.update_last_checked(source, date_utils.get_now_utc())
                logger.info(f"Найдено {new_articles_count} новых сообщений в канале {entity.title}")
            except Exception as e:
                logger.error(f"Ошибка при проверке Telegram-канала {source.target}: {e}")


async def notify_user_about_forbidden_chanel(target, e):
    logger.warning(f"Не удалось получить доступ к каналу с id={target}.\n"
                   f"Убедитесь, что бот имеет права на чтение этого канала.\n", e)
