# Бот-интерфейс для общения с клиентом.
# Позволяет настроить источники, интервал, присылает дайджест

# from scheduler import setup_scheduler
import asyncio
import logging

from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message

from commands import CommandAlias
from config import config
from handlers import register_handlers
from src.db import init_db
from src.digest import get_digest
from src.fetchers.telegram_fetcher import check_telegram_sources

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)
logging.getLogger("sqlalchemy").setLevel(logging.INFO)

logger = logging.getLogger(__name__)

init_db()


async def main():
    try:
        bot = Client(
            config.BOT_SESSION_NAME,
            config.API_ID,
            config.API_HASH,
            bot_token=config.BOT_TOKEN,
            workdir=config.SESSION_DIR,
        )
        logger.info("Бот инициализирован")
    except Exception as e:
        logger.critical(f"Ошибка инициализации бота! {e}")
        return

    try:
        # Создаем клиента для пользователя (для доступа к каналам)
        user_client = Client(
            config.USER_SESSION_NAME,
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            phone_number=config.CLIENT_NUMBER,
            password=config.CLIENT_PASSWORD,
            workdir=config.SESSION_DIR,
        )
        logger.info("Клиент для парсинга telegram каналов инициализирован")
    except Exception as e:
        logger.critical(f"Ошибка инициализации клиента для парсинга telegram каналов! {e}")
        return

    register_handlers(bot)

    async def proxy_dev_test_handler(client: Client, message: Message):
        await check_telegram_sources(user_client, client, message.from_user.id)

    async def get_digest_handler(client: Client, message: Message):
        await get_digest(user_client, client)

    bot.add_handler(MessageHandler(proxy_dev_test_handler, filters.command(CommandAlias.dev_test.value)))
    bot.add_handler(MessageHandler(get_digest_handler, filters.command(CommandAlias.digest.value)))

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
