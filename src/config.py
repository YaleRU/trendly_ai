# Настройки (загрузка API_ID, API_HASH, BOT_TOKEN)
import os
from dotenv import load_dotenv

load_dotenv()

DEFAULT_CHECK_INTERVAL_MINUTES = 5
DEFAULT_SEND_DIGEST_INTERVAL_MINUTES = 10
DEFAULT_MAX_ARTICLES_PER_DIGEST = 10

# ВНИМАНИЕ! ПРИВАТНАЯ ИНФОРМАЦИЯ! Обновляя здесь необходимо обновить .gitignore
SESSION_DIR_NAME = "session"
DATABASE_DIR_NAME = "database"
# ВНИМАНИЕ! ПРИВАТНАЯ ИНФОРМАЦИЯ! Обновляя здесь необходимо обновить .gitignore


# Перенаправляем сессию и базу данных в соответствующие папки
PARENT_DIR_PATH = os.path.dirname(os.path.dirname(__file__))
SESSION_DIR_PATH = os.path.join(PARENT_DIR_PATH, SESSION_DIR_NAME)
DATABASE_DIR_PATH = os.path.join(PARENT_DIR_PATH, DATABASE_DIR_NAME)

for dirname in [SESSION_DIR_PATH, DATABASE_DIR_PATH]:
    if not os.path.exists(dirname):
        os.makedirs(dirname)


class Config:
    # Telegram API Keys
    API_ID = int(os.getenv("API_ID", 0))
    API_HASH = os.getenv("API_HASH")

    # Настройки бота
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    BOT_SESSION_NAME = os.getenv("BOT_SESSION_NAME")

    # Настройки клиента
    CLIENT_NUMBER = os.getenv("CLIENT_NUMBER")
    CLIENT_PASSWORD = os.getenv("CLIENT_PASSWORD")
    USER_SESSION_NAME = os.getenv("USER_SESSION_NAME")

    # Настройки приложения
    SESSION_DIR = SESSION_DIR_PATH
    DATABASE_DIR = DATABASE_DIR_PATH
    DATABASE_NAME = os.getenv("DATABASE_NAME")

    # Пользовательские настройки (в будущем)
    CHECK_INTERVAL_MINUTES = int(os.getenv("CHECK_INTERVAL_MINUTES", DEFAULT_CHECK_INTERVAL_MINUTES))
    SEND_DIGEST_INTERVAL_MINUTES = int(os.getenv("SEND_DIGEST_INTERVAL_MINUTES", DEFAULT_SEND_DIGEST_INTERVAL_MINUTES))
    MAX_ARTICLES_PER_DIGEST = int(os.getenv("MAX_ARTICLES_PER_DIGEST", DEFAULT_MAX_ARTICLES_PER_DIGEST))

    # OpenAI API Key
    # OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # Настройки OpenAI
    # OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo-1106")
    # OPENAI_MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", 500))
    # OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", 0.7))


config = Config()
