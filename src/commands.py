import enum


class CommandAlias(enum.Enum):
    start = "start"
    help = "help"

    add_source = "add"
    remove_source = "remove"
    source_info = "source_info"
    list_sources = "sources"

    digest = "dg"
    dev_test = "dev_test"


class CommandDescription(enum.Enum):
    start = "Начать работу"
    help = "Показать эту справку"

    add_source = f"Добавляет источник для сбора новостей (/{CommandAlias.add_source.value} [link or tg-name])"
    remove_source = "Удаляет источник из отслеживаемых"
    source_info = "Показывает информацию об источнике по его ID"
    list_sources = "Посмотреть список источников и их ID"

    digest = "Выводит дайджест новостей"
    dev_test = "Команда для тестирования в момент разработки"
