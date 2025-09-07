from pyrogram import Client


# ========== ТЗ ============
# 1) Создаем инстанс планировщика
# 2) Обновляем планировщик

# Функция "Обновить планировщик"
#   Выкачать расписание, в нем хранится id пользователя, его настройки дайджеста, дата последней отправки дайджеста и следующей
#   Взять ближайшую дату для нотификации (следующая дата)
#   Поставить таску на нее

# Функция "Таска планировщика"
#   Ищем в базе всех пользователей, у которых дата текущая
#   Для каждого:
#      фетчим источники пользователя, обновляем статьи
#      Показываем статьи за промежуток от прошлой нотификации до следующей
#      Отправляем пользователю
#      Записываем в расписание дату последней отправки(текущую) и следующей (текущая + интервал)
#   Обновляем планировщик

# Функция "Пользователь добавляет дайджест"
#   Записываем его в расписание
#   Обновляем планировщик

def get_digest(user_client: Client, bot: Client):
    # db.get_shedule()

    pass

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
