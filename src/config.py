# Настройки (загрузка API_ID, API_HASH, BOT_TOKEN)
import os
from dotenv import load_dotenv
# Добавьте в начало кода
def get_env_var(name):
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Переменная {name} не найдена в .env файле!")
    return value

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")