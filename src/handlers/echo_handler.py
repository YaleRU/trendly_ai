from pyrogram import Client
from pyrogram.types import Message

async def echo_handler(client: Client, message: Message):
    # Дополнительная проверка на случай, если фильтр не сработает
    if message.text and message.text.startswith('/'):
        return
    await message.reply_text(f"Вы сказали: {message.text}")
