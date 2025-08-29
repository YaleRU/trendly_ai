from pyrogram import Client
from pyrogram.types import Message
import src.handlers._MSG as MSG
from src.database import db



async def start_handler(client: Client, message: Message):
    user = message.from_user
    chat_id = message.chat.id

    conn = db.get_connection()
    cursor = conn.cursor()
    # Добавляем пользователя в БД, если его там нет
    cursor.execute(
        "INSERT OR IGNORE INTO users (user_id, chat_id, first_name, username) VALUES (?, ?, ?, ?)",
        (user.id, chat_id, user.first_name, user.username)
    )
    conn.commit()
    conn.close()

    await message.reply_text(MSG.get_welcome_text(user))
