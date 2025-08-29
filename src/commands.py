import enum


class CommandAlias(enum.Enum):
    start = "start"
    help = "help"
    parse = "parse"
    add_source = "add"


class CommandDescription(enum.Enum):
    start = "Начать работу"
    help = "Показать эту справку"
    parse = "Парсинг сообщений из канала (/" + CommandAlias.parse.value + " @username [limit])"
    add_source = "Добавить источники командой (/" + CommandAlias.add_source.value + " [link or tg-name]"
