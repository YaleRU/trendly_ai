# Настройки (загрузка API_ID, API_HASH, BOT_TOKEN)
import os
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
CLIENT_NUMBER = os.getenv("CLIENT_NUMBER")
CLIENT_PASSWORD = os.getenv("CLIENT_PASSWORD")

# Проверяем, что переменные загружены
if not all([API_ID, API_HASH, CLIENT_NUMBER, CLIENT_PASSWORD]):
    raise ValueError("Не все переменные окружения установлены!")
