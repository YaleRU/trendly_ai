from telethon import events

def register_about_handler(bot):
    # Обработчик команды /about
    @bot.on(events.NewMessage(pattern='/about'))
    async def about_handler(event):
        about_text = """
    О боте:
    • Создан с помощью Telethon
    • Использует Python 3.10+
    • Может парсить сообщения из Telegram-каналов
    """
        await event.respond(about_text)