from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from ..db import crud


def is_working_hours(db: Session, moscow_tz) -> tuple[bool, Optional[str]]:

    now = datetime.now(moscow_tz)

    working_config = crud.get_working_hours_by_day(db, now.weekday())

    if not working_config or not working_config.is_enabled:
        return False, f"Сегодня ({get_day_name(now.weekday())}) не рабочий день"

    try:
        work_start = datetime.strptime(working_config.work_start, "%H:%M").time()
        work_end = datetime.strptime(working_config.work_end, "%H:%M").time()
    except ValueError:
        return False, "Ошибка в конфигурации рабочего времени"

    current_time = now.time()

    if work_start <= current_time <= work_end:
        return True, None
    else:
        return (
            False,
            f"Рабочее время: {working_config.work_start} - {working_config.work_end}",
        )


def get_day_name(day_of_week: int) -> str:
    days = [
        "Понедельник",
        "Вторник",
        "Среда",
        "Четверг",
        "Пятница",
        "Суббота",
        "Воскресенье",
    ]
    return days[day_of_week] if 0 <= day_of_week <= 6 else "Неизвестно"