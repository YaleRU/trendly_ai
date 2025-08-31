import sqlite3
import logging
import os
from enum import Enum
from datetime import datetime
from src.utils import date as date_utils

from config import config

logger = logging.getLogger(__name__)


class SourceType(Enum):
    Telegram = 'tg'
    RSS = 'rss'
    Web = 'web'


class SourceExistsError(Exception):
    def __init__(self, source_url: str):
        super().__init__(f"Источник с таким url уже существует: {source_url}")


class Database:
    def __init__(self, db_path):
        logger.info('Initializing database facade...')
        self.db_path = db_path
        self._init_db()
        logger.info('Database initialized!')

    def _init_db(self):
        logger.info('Initializing database...')
        """Инициализирует таблицы в базе данных."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()

        # Пользователи бота
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT,
                registered_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Источники новостей
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL, -- SourceType(Enum)
                target TEXT NOT NULL, -- Для tg это название канала, НЕ ID, для сайта - ссылка
                is_updating INTEGER DEFAULT 0, -- Идет ли в данный момент обновление источника (чтобы избежать конкуренции)
                last_checked_time DATETIME,
                last_checked_article_id INTEGER
            );
        """)

        # Источники новостей, привязанные к пользователям
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_sources (
                user_id INTEGER NOT NULL,
                source_id INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY (source_id) REFERENCES sources (id) ON DELETE CASCADE,
                PRIMARY KEY (user_id, source_id) -- Комбинированный первичный ключ
            )
        """)

        # Статьи, чтобы избежать дублирования и помнить, что уже отправляли
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_id INTEGER NOT NULL,
                id_in_source TEXT NOT NULL,
                url TEXT NOT NULL UNIQUE,
                title TEXT,
                content TEXT,
                published_at DATETIME NOT NULL,
                FOREIGN KEY (source_id) REFERENCES sources (id) ON DELETE CASCADE
            )
        """)

        # Создаем индексы для ускорения запросов
        cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_source ON sources (target)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sources_user ON user_sources(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_articles_url ON articles(url)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_articles_processed ON articles(published_at)")

        conn.commit()
        conn.close()
        logger.info('Database initialized!')

    def get_connection(self):
        """Возвращает connection к базе данных."""
        return sqlite3.connect(self.db_path)

    def get_active_sources(self, source_type: SourceType):
        """
        Получает источники определенного типа для ВСЕХ пользователей
        """

        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT DISTINCT sources.*
            FROM sources
            INNER JOIN user_sources ON sources.id = user_sources.source_id
            WHERE sources.type = ?
            """,
            (source_type.value,)
        )
        sources = cursor.fetchall()
        conn.close()

        return sources

    def register_user(self, user_id, user_name):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            # Добавляем пользователя в БД, если его там нет
            cursor.execute(
                "INSERT OR IGNORE INTO users (id, username) VALUES (?, ?)",
                (user_id, user_name)
            )
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(e)

    def has_user_source(self, user_id: int, source_id: int):
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM user_sources WHERE user_id = ? AND source_id = ?",
            (user_id, source_id,)
        )
        source = cursor.fetchone()
        conn.close()
        return bool(source)

    def is_source_active(self, source_id: int):
        """
        Возвращает флаг, который указывает, отслеживается ли источник каким либо пользователем
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM user_sources WHERE source_id = ?",
            (source_id,)
        )
        sources = cursor.fetchall()
        conn.close()
        return len(sources) != 0

    def get_user_sources(self, user_id: int, source_type: SourceType | None = None):
        """
        Получает источники определенного типа для конкретного пользователя
        """

        base_query = """
            SELECT sources.* FROM user_sources
            LEFT JOIN sources
            on sources.id = user_sources.source_id
            """

        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        if source_type is None:
            cursor.execute(
                f"{base_query} WHERE user_sources.user_id = ? ",
                (user_id,)
            )
        else:
            cursor.execute(
                f"{base_query} WHERE user_sources.user_id = ? AND sources.type = ? ",
                (user_id, source_type.value,)
            )
        sources = cursor.fetchall()
        conn.close()

        return sources

    def add_user_source(self, user_id: int, source_type: SourceType, source_target: str):
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try:
            # Проверка на существующий источник у пользователя
            cursor.execute(
                """
                SELECT sources.* FROM user_sources 
                LEFT JOIN sources
                ON user_sources.source_id = sources.id
                WHERE user_sources.user_id = ? AND sources.target = ?
                """,
                (user_id, source_target)
            )
            existing_source = cursor.fetchone()
        except Exception as e:
            existing_source = None
            logger.error(f"Ошибка при поиске источника '{source_target}' в БД для пользователя '{user_id}'!")

        # У Пользователя уже есть такой источник
        if existing_source:
            conn.close()
            raise SourceExistsError(source_target)

        try:
            cursor.execute(
                "SELECT id FROM sources WHERE type = ? AND target = ?",
                (source_type, source_target)
            )

            existing_source = cursor.fetchone()

            # Если такой источник уже есть в базе источников, то берем его ID иначе создаем новый
            if existing_source:
                source_id = existing_source['id']
            else:
                cursor.execute(
                    "INSERT OR IGNORE INTO sources (type, target) VALUES (?, ?)",
                    (source_type, source_target)
                )

                conn.commit()
                source_id = cursor.lastrowid

            cursor.execute(
                "INSERT INTO user_sources (user_id, source_id) VALUES (?, ?)",
                (user_id, source_id)
            )
            conn.commit()
        finally:
            conn.close()

    def get_source(self, source_id: int):
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        source = None

        try:
            cursor.execute(
                "SELECT * FROM sources WHERE id=?",
                (source_id,)
            )
            source = cursor.fetchone()
        except Exception as e:
            logger.error(e)
        finally:
            conn.close()

        return source

    def start_source_updating(self, source_id: int):
        self._set_source_updating(source_id, 1)

    def stop_source_updating(self, source_id: int):
        self._set_source_updating(source_id, 0)

    def _set_source_updating(self, source_id: int, is_updating: int):
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "UPDATE sources SET is_updating=? WHERE id=?",
                (is_updating, source_id)
            )
            conn.commit()
        except Exception as e:
            logger.error(e)
        finally:
            conn.close()

    def update_source_last_checked(self, source_id: int,
                                   last_checked_article_id: int | None | type("clear") = None,
                                   last_checked_time: datetime | None | type("clear") = None):
        """Обновляет время последней проверки источника"""
        conn = self.get_connection()
        cursor = conn.cursor()

        query_parts = []
        args = ()

        if last_checked_article_id is not None:
            sub_query = "last_checked_article_id = "
            if last_checked_article_id == "clear":
                sub_query += "NULL"
            else:
                sub_query += "?"
                args = (last_checked_article_id,)
            query_parts.append(sub_query)

        if last_checked_time is not None:
            sub_query = "last_checked_time = "
            if last_checked_time == "clear":
                sub_query += "NULL"
            else:
                sub_query += "?"
                args += (date_utils.get_formatted_datestr(last_checked_time),)
            query_parts.append(sub_query)

        query = f"UPDATE sources SET {', '.join(query_parts)} WHERE id = ?"
        args += (source_id,)

        cursor.execute(query, args)

        conn.commit()
        conn.close()

    def delete_user_source(self, user_id: int, source_id: int):

        conn = self.get_connection()

        try:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM user_sources WHERE user_id = ? AND source_id = ?",
                (user_id, source_id)
            )
            conn.commit()
            conn.close()

            if not self.is_source_active(source_id):
                self.delete_source(source_id)

        except Exception as e:
            logger.error(f"Ошибка при удалении источника данных {source_id} у пользователя {user_id}", e)
            conn.close()

    def delete_source(self, source_id: int):
        conn = self.get_connection()

        try:
            conn.execute("PRAGMA foreign_keys = ON")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM sources WHERE id = ? ", (source_id,))
            conn.commit()
        except Exception as e:
            logger.error("Ошибка удаления источника! ", e)
            raise e
        finally:
            conn.close()

    def get_article(self, article_id: int):
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM articles WHERE id = ?",
            (article_id,)
        )
        article = cursor.fetchone()
        conn.close()
        return article

    def get_articles(self, source_id: int):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM articles WHERE source_id = ?",
            (source_id,)
        )
        articles = cursor.fetchall()
        conn.close()
        return articles

    def add_article(self, article) -> int | None:
        added_article_id = None

        """Сохраняет статьи в БД, если их еще нет"""
        if not article:
            return added_article_id

        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Проверяем, существует ли уже статья с таким URL
            cursor.execute(
                "SELECT id FROM articles WHERE source_id = ? AND id_in_source = ?",
                (article['source_id'], article['id_in_source'])
            )
            existing_article = cursor.fetchone()

            if existing_article:
                added_article_id = existing_article['id']
            else:
                cursor.execute(
                    """
                    INSERT INTO articles 
                    (source_id, id_in_source, url, title, content, published_at) 
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (article['source_id'], article['id_in_source'], article['url'], article['title'],
                     article['content'], article['published_at'])
                )
                conn.commit()
                added_article_id = cursor.lastrowid
        except sqlite3.IntegrityError:
            # Игнорируем ошибки целостности (дубликаты)
            pass
        except Exception as e:
            logger.error(f"Ошибка при сохранении статьи: {e}")

        conn.close()

        return added_article_id


# Создаем глобальный экземпляр БД
db = Database(os.path.join(config.DATABASE_DIR, config.DATABASE_NAME))
