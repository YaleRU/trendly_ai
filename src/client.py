# import os
# import re
# from pyrogram import Client, filters
# from pyrogram.types import Message
# from config import API_ID, API_HASH, CLIENT_NUMBER, CLIENT_PASSWORD, BOT_TOKEN
#
# # Указываем новый путь к файлу сессии (на уровень выше в папке session)
# SESSION_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'session')
#
# if not os.path.exists(SESSION_DIR):
#     os.makedirs(SESSION_DIR)
#
# app = Client("my_account",
#              API_ID,
#              API_HASH,
#              phone_number=CLIENT_NUMBER,
#              password=CLIENT_PASSWORD,
#              workdir=SESSION_DIR,
#              )
#
#
# # Обработчик команды /parse
# @app.on_message(filters.command("parse"))
# async def parse_handler(client: Client, message: Message):
#     # Проверяем, есть ли текст команды
#     if not message.text or len(message.text.split()) < 2:
#         await message.reply_text("""
# Использование команды /parse:
# /parse <username_канала> [количество_сообщений]
#
# Примеры:
# /parse @python_telethon 10
# /parse news_channel 5
# """)
#         return
#
#     try:
#         # Извлекаем параметры из команды
#         parts = message.text.split()
#         channel_username = parts[1]
#         limit = int(parts[2]) if len(parts) > 2 else 10
#
#         # Убираем @ из username если есть
#         if channel_username.startswith('@'):
#             channel_username = channel_username[1:]
#
#         # Проверяем лимит
#         if limit > 50:
#             await message.reply_text("Максимальное количество сообщений для парсинга - 50")
#             return
#
#         # Уведомляем о начале парсинга
#         progress_msg = await message.reply_text(f"Начинаю парсинг {limit} сообщений из {channel_username}...")
#
#         # Получаем информацию о канале
#         try:
#             chat = await client.get_chat(channel_username)
#         except Exception as e:
#             await message.reply_text(f"Не могу найти канал {channel_username}. Ошибка: {str(e)}")
#             return
#
#         # Собираем сообщения
#         messages = []
#         async for msg in client.get_chat_history(chat.id, limit=limit):
#             messages.append(msg)
#
#         if not messages:
#             await message.reply_text("Не удалось получить сообщения из канала")
#             return
#
#         # Формируем результат
#         result = f"Последние {len(messages)} сообщений из {chat.title}:\n\n"
#
#         for i, msg in enumerate(messages, 1):
#             if msg.text:
#                 # Очищаем текст от лишних переносов
#                 text = re.sub(r'\n+', ' ', msg.text)
#                 # Обрезаем длинные сообщения
#                 text = text[:200] + "..." if len(text) > 200 else text
#                 result += f"{i}. {text}\n\n"
#             elif msg.caption:
#                 # Если есть подпись к медиа
#                 text = re.sub(r'\n+', ' ', msg.caption)
#                 text = text[:200] + "..." if len(text) > 200 else text
#                 result += f"{i}. [Медиа] {text}\n\n"
#             else:
#                 result += f"{i}. [Медиа-сообщение]\n\n"
#
#         # Отправляем результат
#         if len(result) > 4096:
#             # Разбиваем на части если сообщение слишком длинное
#             parts = [result[i:i + 4096] for i in range(0, len(result), 4096)]
#             for part in parts:
#                 await message.reply_text(part)
#         else:
#             await message.reply_text(result)
#
#         # Удаляем сообщение о прогрессе
#         await progress_msg.delete()
#
#     except Exception as e:
#         error_msg = f"Ошибка при парсинге: {str(e)}"
#         await message.reply_text(error_msg)
#
#
#
#
# # Запуск бота
# if __name__ == "__main__":
#     print("Бот запущен...")
#     app.run()
