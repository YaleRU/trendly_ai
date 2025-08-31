from pyrogram import Client
from pyrogram.types import Message
import src.handlers._MSG as MSG
from src.database import db


async def start_handler(_client: Client, message: Message):
    user = message.from_user
    # chat_id = message.chat.id

    db.register_user(user.id, user.username)

    await message.reply_text(MSG.get_welcome_text(user))
