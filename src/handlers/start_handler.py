import logging

from pyrogram import Client
from pyrogram.types import Message

import src.handlers._MSG as MSG
from src.db import SessionLocal
from src.services import UserService

logger = logging.getLogger(__name__)


async def start_handler(_client: Client, message: Message):
    user = message.from_user
    chat_id = message.chat.id

    service = UserService(SessionLocal())

    user = service.get_or_create_user(user.id,
                                      chat_id=chat_id,
                                      username=user.username,
                                      first_name=user.first_name,
                                      last_name=user.last_name
                                      )

    logger.info(f"User {user.username} started with chat_id {user.chat_id}")

    await message.reply_text(MSG.get_welcome_text(message.from_user.mention))
