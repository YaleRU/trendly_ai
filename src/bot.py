# Бот-интерфейс для общения с клиентом.
# Позволяет настроить источники, интервал, присылает дайджест

import logging
from pyrogram import Client, filters
from config import config
from handlers import register_handlers
from scheduler import setup_scheduler
import asyncio

from pyrogram.types import Message
from pyrogram.handlers import MessageHandler
from src.fetchers.telegram_fetcher import check_telegram_sources
from commands import CommandAlias

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def main():
    logger.info("Запуск бота...")
    bot = Client(
        config.BOT_SESSION_NAME,
        config.API_ID,
        config.API_HASH,
        bot_token=config.BOT_TOKEN,
        workdir=config.SESSION_DIR,
    )

    logger.info("Запуск клиента...")
    # Создаем клиента для пользователя (для доступа к каналам)
    user_client = Client(
        config.USER_SESSION_NAME,
        api_id=config.API_ID,
        api_hash=config.API_HASH,
        phone_number=config.CLIENT_NUMBER,
        password=config.CLIENT_PASSWORD,
        workdir=config.SESSION_DIR,
    )

    register_handlers(bot)

    async def proxy_dev_test_handler(client: Client, message: Message):
        await check_telegram_sources(user_client, client)

    bot.add_handler(MessageHandler(proxy_dev_test_handler, filters.command(CommandAlias.dev_test.value)))

    # Настраиваем и запускаем планировщик (в отдельной задаче asyncio)
    # await setup_scheduler(user_client, bot)

    try:
        await bot.start()
        logger.info("Бот запущен!")

        await user_client.start()
        logger.info("Клиент запущен!")

        # Бесконечный цикл для поддержания работы бота
        await asyncio.Event().wait()
    except Exception as e:
        logger.critical(f"Ошибка при запуске бота: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
