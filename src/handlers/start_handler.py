from telethon import events

@events.register(events.NewMessage(pattern='/start'))
async def start_handler(event):
    await event.respond('Привет! Я простой бот. Отправь мне любое сообщение, и я его повторю!')