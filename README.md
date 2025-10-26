## Трендовый бот

---
1. pip install -r requirements.txt
---


### Запуск
1. Python 3.11+
2. `pip install -r requirements.txt`
3. Создайте `.env` в корне проекта:
```
API_ID=...
API_HASH=...
BOT_TOKEN=...
OPENAI_API_KEY=   # можно не указывать, тогда дайджесты будут без ИИ-выжимки
OPENAI_MODEL=gpt-4o-mini
OPENAI_MAX_TOKENS=300
OPENAI_TEMPERATURE=0.2
```
4. `python -m src.bot`
