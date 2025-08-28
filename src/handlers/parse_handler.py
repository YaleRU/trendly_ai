from pyrogram import Client
from pyrogram.types import Message

async def parse_handler(client: Client, message: Message):
    await message.reply_text("Команда /parse в процессе разработки...")

