from pyrogram import Client
from pyrogram.types import Message

from ._MSG import help_text


async def help_handler(_client: Client, message: Message):
    await message.reply_text(help_text)
