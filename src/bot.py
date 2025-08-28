# Бот-интерфейс для общения с клиентом.
# Позволяет настроить источники, интервал, присылает дайджест

import logging
from pyrogram import Client
from config import config
from handlers import register_handlers

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

bot = Client(
    config.BOT_SESSION_NAME,
    config.API_ID,
    config.API_HASH,
    bot_token=config.BOT_TOKEN,
    workdir=config.SESSION_DIR,
)

# Запуск бота
if __name__ == "__main__":
    register_handlers(bot)
    logger.info("Бот запущен...")

    bot.run()
#
# async def main():
#     async with bot:
#         register_handlers(bot)
#     print("Бот запущен...")
#
#
# bot.run(main())