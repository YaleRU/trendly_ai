from telethon import events

from .start_handler import register_start_handler
from .about_handler import register_about_handler
from .help_handler import register_help_handler
from .parse_handler import register_parse_handler
from .parse_stats_handler import register_parse_stats_handler

def register_handlers(bot):
    register_start_handler(bot)
    register_about_handler(bot)
    register_help_handler(bot)
    register_parse_handler(bot)
    register_parse_stats_handler(bot)

    # Обработчик всех текстовых сообщений (эхо)
    @bot.on(events.NewMessage)
    async def echo_handler(event):
        # Пропускаем команды
        if (hasattr(event, 'message') and
                hasattr(event.message, 'text') and
                event.message.text and
                event.message.text.startswith('/')):
            return

        # Отвечаем тем же текстом
        if hasattr(event, 'message') and hasattr(event.message, 'text'):
            await event.respond(f'Вы сказали: {event.message.text}')