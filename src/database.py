import sqlite3
import logging
import os
from config import config

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path):
        logger.info('Initializing database facade...')
        self.db_path = db_path
        self._init_db()
        logger.info('Database initialized!')

    def _init_db(self):
        logger.info('Initializing database...')
        conn = sqlite3.connect(self.db_path)
        """Инициализирует таблицы в базе данных."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Пользователи бота
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                chat_id INTEGER NOT NULL,
                first_name TEXT,
                username TEXT,
                registered_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Источники новостей, привязанные к пользователям
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                type TEXT NOT NULL, -- 'telegram', 'rss', 'web'
                url TEXT NOT NULL,
                title TEXT, -- Название канала/сайта (для удобства)
                last_checked DATETIME,
                FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
            )
        """)

        # Статьи, чтобы избежать дублирования и помнить, что уже отправляли
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_id INTEGER NOT NULL,
                url TEXT NOT NULL UNIQUE, -- URL или уникальный ID из Telegram
                title TEXT,
                content TEXT,
                summary TEXT,
                published_at DATETIME,
                processed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (source_id) REFERENCES sources (id) ON DELETE CASCADE
            )
        """)

        # Создаем индексы для ускорения запросов
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_articles_url ON articles(url)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_articles_processed ON articles(processed_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sources_user ON sources(user_id)")

        conn.commit()
        conn.close()
        logger.info('Database initialized!')

    def get_connection(self):
        """Возвращает connection к базе данных."""
        return sqlite3.connect(self.db_path)

# Создаем глобальный экземпляр БД
db = Database(os.path.join(config.DATABASE_DIR, config.DATABASE_NAME))