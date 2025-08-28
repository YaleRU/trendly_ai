from telethon import events

def register_start_handler(bot):
    # Обработчик команды /start
    @bot.on(events.NewMessage(pattern='/start'))
    async def start_handler(event):
        welcome_text = """
Привет! Я бот с функцией парсинга Telegram-каналов.

Доступные команды:
/start - Начать работу
/help - Показать справку
/about - Информация о боте
/parse @username [limit] - Парсинг сообщений из канала
/parse_stats @username - Статистика канала
"""
        await event.respond(welcome_text)