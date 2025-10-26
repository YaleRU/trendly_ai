from typing import Optional

from pyrogram.types import Message

from src.commands import CommandAlias
from src.db import User, SessionLocal
from src.db.repositories import UserRepository


class MissingEntityError(Exception):
    def __init__(self, msg: Optional[str] = None):
        super().__init__(f"Искомой сущности не найдено!\n", msg)


async def get_user_by_telegram_id_safe(message: Message, telegram_id: int) -> User:
    user_repo = UserRepository(SessionLocal())
    user = user_repo.get_by_telegram_id(telegram_id)

    if not user:
        await message.reply_text("Сначала зарегистрируйтесь с помощью /" + CommandAlias.start.value)
        raise MissingEntityError(f"User с telegram_id={telegram_id}")

    return user
