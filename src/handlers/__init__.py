import logging
from pyrogram import filters
from pyrogram.handlers import MessageHandler

from .start_handler import start_handler
from .help_handler import help_handler
from .parse_handler import parse_handler
from .echo_handler import echo_handler

logger = logging.getLogger(__name__)

def non_command_filter(_, __, m):
    return (
        m.text and
        not m.text.startswith('/') and
        not m.text.startswith('!') and
        not m.text.startswith('.')
    )

non_command = filters.create(non_command_filter)

def register_handlers(bot):
    logger.info('Starting handlers registration...')

    bot.add_handler(MessageHandler(start_handler, filters.command("start")))
    bot.add_handler(MessageHandler(help_handler, filters.command("help")))
    bot.add_handler(MessageHandler(parse_handler, filters.command("parse")))
    bot.add_handler(MessageHandler(echo_handler, non_command))

    logger.info('Handlers registered!')
