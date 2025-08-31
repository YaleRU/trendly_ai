from src.commands import CommandAlias, CommandDescription

available_commands_text = """
Доступные команды:\n
""" + '\n'.join('/' + c.value + ' - ' + CommandDescription[c.name].value for c in CommandAlias)

help_text = available_commands_text

welcome_text = """
👋 Привет! 
Я бот с функцией парсинга Telegram-каналов.
Для справки нажмите /""" + CommandAlias.help.value


def get_welcome_text(user):
    return (f"Привет, {user.mention}!\n\n"
            f"Я бот для создания персональных дайджестов новостей.\n"
            f"Для справки нажмите /{CommandAlias.help.value}.\n"
            f"Добавь источники командой /{CommandAlias.add_source.value}.")

