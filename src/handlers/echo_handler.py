from telethon import events


@events.register(events.NewMessage)
async def echo_handler(event):
    # Не отвечаем на служебные сообщения и команды
    if event.text and event.text.startswith('/'):
        return

    # Отвечаем тем же текстом
    await event.respond(f'Вы сказали: {event.text}')