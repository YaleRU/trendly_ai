# Импортируем все модели для удобного доступа
from .user import User
from .source import Source, SourceType
from .article import Article
from .association_tables import user_source_association

# Список всех моделей для импорта в других местах
__all__ = ["User", "Source", "SourceType", "Article", "user_source_association"]
