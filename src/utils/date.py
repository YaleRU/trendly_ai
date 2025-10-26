from datetime import datetime, timezone, timedelta

# Формат, в котором дата хранится в БД
DB_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

# Объект часового пояса UTC, используемый по всему проекту
UTC = timezone.utc


def get_smallest_utc() -> datetime:
    return as_utc(datetime.fromtimestamp(0))


def get_now_utc() -> datetime:
    return datetime.now(timezone.utc)


def get_now_local() -> datetime:
    return datetime.now()


def as_utc(dt: datetime | str) -> datetime:
    return _get_dt_from_date_or_string(dt).replace(tzinfo=timezone.utc)


def to_utc(local_dt: datetime | str) -> datetime:
    local_dt = _get_dt_from_date_or_string(local_dt)
    offset = local_dt.astimezone().utcoffset()
    return as_utc(local_dt - offset)


def to_local(utc_datetime: datetime | str) -> datetime:
    offset = datetime.now(timezone.utc).astimezone().utcoffset()
    return as_utc(_get_dt_from_date_or_string(utc_datetime)) + offset


def get_formatted_datestr(date: datetime) -> str:
    """
        Превращает объект datetime в строку с форматированной датой.
        Формат соответствует формату хранения даты в БД.
        """
    return date.strftime(DB_DATETIME_FORMAT)


def get_dt_from_datestr(date_str: str) -> datetime:
    """
    Превращает строку с форматированной датой в объект datetime
    """
    return datetime.strptime(date_str, DB_DATETIME_FORMAT)


def _get_dt_from_date_or_string(date: datetime | str) -> datetime:
    return date if isinstance(date, datetime) else get_dt_from_datestr(date)


if __name__ == '__main__':
    def log(name: str, d):
        print(f"{name}: {d} {type(d)}")


    log('utc', get_formatted_datestr(get_now_utc()))
    log('local', get_formatted_datestr(get_now_local()))
    log('utc from local', get_formatted_datestr(to_utc(get_now_local())))
    log('local from utc', get_formatted_datestr(to_local(get_now_utc())))
    log('utc from str', get_dt_from_datestr(get_formatted_datestr(get_now_utc())))
    log('smallest utc', get_formatted_datestr(get_smallest_utc()))
