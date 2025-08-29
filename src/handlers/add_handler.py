from pyrogram import Client
from pyrogram.types import Message

async def add_handler(client: Client, message: Message):
    await message.reply_text("Команда /add в процессе разработки...")

