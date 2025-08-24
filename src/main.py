import os
from telethon import TelegramClient, events
from dotenv import load_dotenv

load_dotenv()
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Создаём клиент
bot = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Реакция на команду /start
@bot.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    await event.respond("👋 Привет! Я твой новый бот на Telethon!")
    raise events.StopPropagation

# Реакция на любое сообщение
@bot.on(events.NewMessage)
async def echo_handler(event):
    await event.respond(f"Ты написал: {event.text}")

print("✅ Бот запущен!")
bot.run_until_disconnected()




