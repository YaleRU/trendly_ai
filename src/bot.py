from telethon import TelegramClient, events
from config import API_ID, API_HASH, BOT_TOKEN
import os
import sys

# Добавляем путь к src для импортов
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Проверяем, что переменные загружены
if not all([API_ID, API_HASH, BOT_TOKEN]):
    raise ValueError("Не все переменные окружения установлены!")

# Указываем новый путь к файлу сессии (на уровень выше в папке session)
SESSION_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'session', 'bot.session')

SESSION_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'session')
if not os.path.exists(SESSION_DIR):
    os.makedirs(SESSION_DIR)

# Создаем клиент
bot = TelegramClient('../session/bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Импортируем обработчики
from handlers.start_handler import start_handler
from handlers.echo_handler import echo_handler
from handlers.help_handler import help_handler

# Регистрируем обработчики
bot.add_event_handler(start_handler)
bot.add_event_handler(echo_handler)
bot.add_event_handler(help_handler)

# Запуск бота
if __name__ == '__main__':
    print('Бот запущен...')
    bot.run_until_disconnected()


