import logging

from sqlalchemy import create_engine
from sqlalchemy.event import listens_for
from sqlalchemy.orm import sessionmaker, scoped_session

from src.config import config
from src.db.models import User
from src.db.base import Base

logger = logging.getLogger(__name__)

# Создаем движок базы данных
engine = create_engine(config.DSN)

# Создаем фабрику сессий
SessionLocal = scoped_session(sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
))


def init_db():
    """Инициализирует базу данных, создавая все таблицы"""

    # Включаем внешние ключи для SQLite
    @listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    try:
        # TODO: Убрать
        # Base.metadata.drop_all(engine)
        Base.metadata.create_all(bind=engine)
        logger.info('Database initialized with SQLAlchemy 2.0!')
    except Exception as e:
        logger.critical('Database initialization failed!', e)


# Импортируем модели после создания Base
from src.db.models import User, Source, Article, SourceType
