from telethon import events
import re

def register_parse_stats_handler(bot):
    # Обработчик команды /parse_stats
    @bot.on(events.NewMessage(pattern='/parse_stats'))
    async def parse_stats_handler(event):
        # Получаем текст сообщения
        if not hasattr(event, 'message') or not hasattr(event.message, 'text'):
            await event.respond("Команда /parse_stats должна быть текстовым сообщением")
            return

        message_text = event.message.text

        # Используем регулярное выражение для извлечения параметров
        match = re.match(r'/parse_stats\s+(@?\w+)', message_text)

        if not match:
            await event.respond("Использование: /parse_stats @username_канала")
            return

        try:
            channel_username = match.group(1)
            # Убираем @ если есть
            if channel_username.startswith('@'):
                channel_username = channel_username[1:]

            progress_msg = await event.respond(f"Начинаю анализ канала {channel_username}...")

            # Получаем информацию о канале
            try:
                entity = await bot.get_entity(channel_username)
            except ValueError:
                # Пробуем найти с @
                try:
                    entity = await bot.get_entity('@' + channel_username)
                except ValueError:
                    await event.respond(f"Не могу найти канал {channel_username}")
                    try:
                        await progress_msg.delete()
                    except:
                        pass
                    return

            # Получаем историю сообщений для анализа
            messages = await bot.get_messages(entity, limit=100)

            if not messages:
                await event.respond("Не удалось получить сообщения из канала")
                try:
                    await progress_msg.delete()
                except:
                    pass
                return

            # Анализируем сообщения
            total_messages = len(messages)
            text_messages = sum(1 for m in messages if (m.text or m.message) and (m.text or m.message).strip())
            media_messages = total_messages - text_messages

            # Считаем среднюю длину текстовых сообщений
            text_lengths = [len(m.text or m.message or "") for m in messages if
                            (m.text or m.message) and (m.text or m.message).strip()]
            avg_length = sum(text_lengths) / len(text_lengths) if text_lengths else 0

            # Формируем статистику
            stats = f"""
Статистика канала {channel_username} (последние 100 сообщений):

Всего сообщений: {total_messages}
Текстовых сообщений: {text_messages}
Медиа-сообщений: {media_messages}
Процент текстовых сообщений: {text_messages / total_messages * 100:.1f}%
Процент медиа-сообщений: {media_messages / total_messages * 100:.1f}%
Средняя длина текстового сообщения: {avg_length:.0f} символов
"""
            await event.respond(stats)
            try:
                await progress_msg.delete()
            except:
                pass

        except Exception as e:
            error_msg = f"Ошибка при анализе канала: {str(e)}"
            await event.respond(error_msg)
            try:
                await progress_msg.delete()
            except:
                pass