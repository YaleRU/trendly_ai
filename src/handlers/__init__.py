import logging
from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler

from src.commands import CommandAlias
from .start_handler import start_handler
from .help_handler import help_handler
from .echo_handler import echo_handler
from .add_source_handler import add_source_handler
from .list_sources_handler import list_sources_handler
from .source_info_handler import source_info_handler
from .remove_source_handler import remove_source_handler

logger = logging.getLogger(__name__)


def non_command_filter(_, __, m):
    return (
            m.text and
            not m.text.startswith('/') and
            not m.text.startswith('!') and
            not m.text.startswith('.')
    )


non_command = filters.create(non_command_filter)


def register_handlers(bot: Client):
    logger.info('Starting handlers registration...')

    bot.add_handler(MessageHandler(start_handler, filters.command(CommandAlias.start.value)))
    bot.add_handler(MessageHandler(help_handler, filters.command(CommandAlias.help.value)))
    bot.add_handler(MessageHandler(add_source_handler, filters.command(CommandAlias.add_source.value)))
    bot.add_handler(MessageHandler(list_sources_handler, filters.command(CommandAlias.list_sources.value)))
    bot.add_handler(MessageHandler(source_info_handler, filters.command(CommandAlias.source_info.value)))
    bot.add_handler(MessageHandler(remove_source_handler, filters.command(CommandAlias.remove_source.value)))
    bot.add_handler(MessageHandler(echo_handler, non_command))

    logger.info('Handlers registered!')
