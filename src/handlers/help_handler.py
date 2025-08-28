from telethon import events

def register_help_handler(bot):
    # Обработчик команды /help
    @bot.on(events.NewMessage(pattern='/help'))
    async def help_handler(event):
        help_text = """
Доступные команды:
/start - Начать работу
/help - Показать эту справку
/about - Информация о боте
/parse @username [limit] - Парсинг сообщений из канала
/parse_stats @username - Статистика канала
"""
        await event.respond(help_text)