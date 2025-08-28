from telethon import events
import asyncio
import re

def register_parse_handler(bot):
    # Обработчик команды /parse
    @bot.on(events.NewMessage(pattern='/parse'))
    async def parse_handler(event):

        # Получаем текст сообщения
        if not hasattr(event, 'message') or not hasattr(event.message, 'text'):
            await event.respond("Команда /parse должна быть текстовым сообщением")
            return

        message_text = event.message.text

        # Используем регулярное выражение для извлечения параметров
        match = re.match(r'/parse\s+(@?\w+)\s*(\d+)?', message_text)

        if not match:
            await event.respond("""
Использование команды /parse:
/parse <username_канала> [количество_сообщений]

Примеры:
/parse python_telethon - 10 последних сообщений
/parse news_channel 5 - 5 последних сообщений

Примечание: бот должен быть участником канала!
""")
            return

        message = event.message

        try:
            channel_username = match.group(1)
            # Убираем @ если есть
            if channel_username.startswith('@'):
                channel_username = channel_username[1:]

            limit = int(match.group(2)) if match.group(2) else 10

            # Проверяем лимит
            if limit > 50:
                await event.respond("Максимальное количество сообщений для парсинга - 50")
                return

            # Уведомляем о начале парсинга
            progress_msg = await event.respond(f"Начинаю парсинг {limit} сообщений из {channel_username}...")

            # Получаем информацию о канале
            try:
                entity = await bot.get_entity(channel_username)
            except ValueError:
                # Пробуем найти с @
                try:
                    entity = await bot.get_entity('@' + channel_username)
                except ValueError:
                    await bot.send_message(message.sender_id,
                                           f"Не могу найти канал {channel_username}. Убедитесь, что:")
                    await bot.send_message(message.sender_id, "1. Канал является публичным")
                    await bot.send_message(message.sender_id, "2. Вы указали правильное имя канала")
                    try:
                        await bot.delete_messages(message.sender_id, [progress_msg.id])
                    except:
                        pass
                    return

            # Для ботов используем другой подход - получаем сообщения через итератор
            # но с ограничениями, так как боты не могут использовать GetHistoryRequest
            result = f"Последние сообщения из {channel_username}:\n\n"
            count = 0

            # Получаем сообщения через итератор (ограниченный функционал для ботов)
            async for msg in bot.iter_messages(entity, limit=limit):
                if count >= limit:
                    break

                if msg.text:
                    # Очищаем текст от лишних переносов
                    text = re.sub(r'\n+', ' ', msg.text)
                    # Обрезаем длинные сообщения
                    text = text[:200] + "..." if len(text) > 200 else text
                    result += f"{count + 1}. {text}\n\n"
                elif hasattr(msg, 'message') and msg.message:
                    # Если есть message вместо text
                    text = re.sub(r'\n+', ' ', msg.message)
                    text = text[:200] + "..." if len(text) > 200 else text
                    result += f"{count + 1}. {text}\n\n"
                else:
                    result += f"{count + 1}. [Медиа-сообщение]\n\n"

                count += 1

            if count == 0:
                result = "Не удалось получить сообщения из канала. Возможные причины:\n"
                result += "1. Канал приватный (ботам недоступен)\n"
                result += "2. Бот не является участником канала\n"
                result += "3. В канале нет сообщений"

            # Отправляем результат (разбиваем на части, если слишком длинный)
            if len(result) > 4000:
                parts = [result[i:i + 4000] for i in range(0, len(result), 4000)]
                for part in parts:
                    await bot.send_message(message.sender_id, part)
                    await asyncio.sleep(1)  # Задержка между сообщениями
            else:
                await bot.send_message(message.sender_id, result)

            # Удаляем сообщение о прогресse
            try:
                await bot.delete_messages(message.sender_id, [progress_msg.id])
            except:
                pass

        except Exception as e:
            error_msg = f"Ошибка при парсинге: {str(e)}"
            await bot.send_message(message.sender_id, error_msg)
            # Пытаемся удалить сообщение о прогрессе, если оно есть
            try:
                await bot.delete_messages(message.sender_id, [progress_msg.id])
            except:
                pass

