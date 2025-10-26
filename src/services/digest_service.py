from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta

from pyrogram import Client
from sqlalchemy.orm import Session
import logging
from src.db.models import User, Article, Source
from src.summarizer import summarize_text
import src.utils.date as date_utils

logger = logging.getLogger(__name__)


class DigestService:
    """Сервис для генерации дайджестов новостей"""

    def __init__(self, db: Session):
        self.db = db

    def get_inspired_users(self) -> list[User]:
        return self.db.query(User).filter((User.next_digest_time < date_utils.get_now_utc())).all()

    def has_inspired_users(self) -> bool:
        return len(self.get_inspired_users()) > 0
    
    def get_user_articles(self, user_id: int, hours: int = 24) -> List[Article]:
        """Получает статьи пользователя за указанный период"""
        time_threshold = datetime.now() - timedelta(hours=hours)

        # Получаем статьи из всех источников пользователя
        articles = self.db.query(Article). \
            join(Article.source). \
            join(Source.users). \
            filter(
            User.id == user_id,
            Article.published_at >= time_threshold
        ). \
            order_by(Article.published_at.desc()). \
            all()

        return articles

    def get_articles_grouped_by_source(self, user_id: int, hours: int = 24) -> Dict[Source, List[Article]]:
        """Получает статьи пользователя, сгруппированные по источникам"""
        articles = self.get_user_articles(user_id, hours)

        # Группируем статьи по источникам
        grouped_articles = {}
        for article in articles:
            if article.source not in grouped_articles:
                grouped_articles[article.source] = []
            grouped_articles[article.source].append(article)

        return grouped_articles

    async def generate_digest(self, user_id: int, hours: int = 24) -> Optional[str]:
        """Генерирует дайджест новостей для пользователя"""
        try:
            # Получаем статьи, сгруппированные по источникам
            grouped_articles = self.get_articles_grouped_by_source(user_id, hours)

            if not grouped_articles:
                return None

            # Формируем дайджест
            digest_parts = ["📰 <b>Ваш персональный дайджест новостей</b>\n\n"]

            for source, articles in grouped_articles.items():
                # Добавляем заголовок источника
                source_title = source.title or source.target
                digest_parts.append(f"📢 <b>{source_title}</b>\n")

                # Добавляем статьи этого источника
                for i, article in enumerate(articles, 1):
                    # Суммаризируем статью (если еще не суммирована)
                    if not article.summary:
                        article.summary = await summarize_text(article.content)
                        self.db.commit()

                    summary = article.summary or article.content[:200] + "..."

                    digest_parts.append(
                        f"{i}. <b>{article.title}</b>\n"
                        f"{summary}\n"
                    )

                digest_parts.append("\n")

            digest_parts.append(
                "\n💡 <i>Используйте /settings чтобы изменить настройки дайджеста</i>"
            )

            return "".join(digest_parts)

        except Exception as e:
            logger.error(f"Ошибка при генерации дайджеста для пользователя {user_id}: {e}")
            return None

    def get_articles_count(self, user_id: int, hours: int = 24) -> int:
        """Возвращает количество новых статей пользователя"""
        time_threshold = datetime.now() - timedelta(hours=hours)

        count = self.db.query(Article). \
            join(Article.source). \
            join(Source.users). \
            filter(
            User.id == user_id,
            Article.published_at >= time_threshold
        ). \
            count()

        return count

    async def send_digest(self, bot_client: Client):

        def get_new_articles(_source: Source) -> List[Article]:
            # статьи, у которых дата добавления в базу больше чем дата последней нотификации
            pass

        async def send_new_articles(user: User, _articles: Dict[Source, List[Article]]):
            await bot_client.send_message(chat_id=user.chat_id, text="Новые статьи")

        def update_last_digest_time(user: User):
            user.last_digest_time = date_utils.get_now_utc()
            self.db.commit()
            pass

        articles_by_source: Dict[Source, List[Article]] = {}

        for user in self.get_inspired_users():
            for source in user.sources:
                articles_by_source[source] = get_new_articles(source)
            await send_new_articles(user, articles_by_source)
            update_last_digest_time(user)

# Функция "Пользователь добавляет дайджест"
#   Записываем его в расписание
#   Обновляем планировщик

# # Format digest message
#             digest_text = "📰 Your Daily News Digest\n\n"
#             for article in articles:
#                 digest_text += f"*{article.title}*\n"
#                 digest_text += f"{article.summary}\n"
#                 digest_text += f"[Read more]({article.url})\n\n"
#
#             # Send via Telegram Bot (using bot instance, careful with async here)
#             # In a real scenario, you'd use a separate task or an async method to send.
#             # For simplicity, we'll assume a synchronous call is possible.
#             from bot_core import bot
#             asyncio.run(bot.send_message(user.id, digest_text, parse_mode="Markdown"))
#             logger.info(f"Digest sent to user {user.id}")
