from telethon import events

@events.register(events.NewMessage(pattern='/help'))
async def help_handler(event):
    help_text = """
Доступные команды:
/start - Начать работу
/help - Показать справку
/menu - Показать меню
"""
    await event.respond(help_text)