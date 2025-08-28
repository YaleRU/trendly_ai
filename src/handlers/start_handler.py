from pyrogram import Client
from pyrogram.types import Message
from ._MSG import welcome_text


async def start_handler(client: Client, message: Message):
    await message.reply_text(welcome_text)
