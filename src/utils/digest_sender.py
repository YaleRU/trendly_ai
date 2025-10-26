import logging
from typing import Dict

from pyrogram import Client
from pyrogram.enums import ParseMode
from sqlalchemy.orm import Session

from ..services.digest_service import DigestService

logger = logging.getLogger(__name__)


async def send_digest_to_user(bot_client: Client, db: Session, user_id: int, chat_id: int) -> bool:
    """Отправляет дайджест пользователю"""
    try:
        digest_service = DigestService(db)
        digest_text = await digest_service.generate_digest(user_id)

        if not digest_text:
            logger.info(f"Нет новых статей для пользователя {user_id}")
            return False

        # Отправляем дайджест
        await bot_client.send_message(
            chat_id=chat_id,
            text=digest_text,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True
        )

        logger.info(f"Дайджест отправлен пользователю {user_id}")
        return True

    except Exception as e:
        logger.error(f"Ошибка при отправке дайджеста пользователю {user_id}: {e}")
        return False


async def send_digest_to_all_users(bot_client: Client, db: Session) -> Dict[str, int]:
    """Отправляет дайджест всем активным пользователям"""
    from src.db.models import User

    results = {
        'total': 0,
        'success': 0,
        'failed': 0,
        'no_articles': 0
    }

    # Получаем всех активных пользователей
    active_users = db.query(User).filter(User.is_active == True).all()
    results['total'] = len(active_users)

    for user in active_users:
        try:
            has_articles = await send_digest_to_user(bot_client, db, user.id, user.chat_id)

            if has_articles:
                results['success'] += 1
            else:
                results['no_articles'] += 1

        except Exception as e:
            logger.error(f"Ошибка при отправке дайджеста пользователю {user.id}: {e}")
            results['failed'] += 1

    return results
