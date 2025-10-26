import logging
from typing import Dict

from pyrogram import Client
from pyrogram.enums import ParseMode
from sqlalchemy.orm import Session

from ..services.digest_service import DigestService
from ..db.models import User

logger = logging.getLogger(__name__)


async def send_digest_to_user(bot_client: Client, db: Session, user_id: int, chat_id: int) -> bool:
    try:
        digest_service = DigestService(db)
        digest_text = await digest_service.generate_digest(user_id=user_id, hours=24)
        if not digest_text:
            return False

        await bot_client.send_message(chat_id, digest_text, parse_mode=ParseMode.HTML, disable_web_page_preview=True)

        user = db.query(User).get(user_id)  # type: ignore[call-arg]
        if user:
            digest_service.mark_digest_sent(user)
        return True
    except Exception:
        logger.exception("send_digest_to_user failed")
        return False


async def send_digest_to_all_users(bot_client: Client, db: Session) -> Dict[str, int]:
    results = {"total": 0, "success": 0, "no_articles": 0, "failed": 0}
    digest_service = DigestService(db)
    users_due = digest_service.get_active_users_due()
    results["total"] = len(users_due)
    for user in users_due:
        try:
            sent = await send_digest_to_user(bot_client, db, user.id, user.chat_id)  # type: ignore[attr-defined]
            if sent:
                results["success"] += 1
            else:
                results["no_articles"] += 1
        except Exception:
            logger.exception("digest to user failed")
            results["failed"] += 1
    return results
