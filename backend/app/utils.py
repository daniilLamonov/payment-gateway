from datetime import datetime, time
from pytz import timezone as tz
import qrcode
import io
import base64
from typing import Optional
from sqlalchemy.orm import Session
from . import crud
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse


def build_payment_url_with_amount(base_url: str, amount: int, parameter_name: str = "sum") -> str:
    """
    Построить URL для оплаты с указанием суммы.

    Args:
        base_url: Базовая ссылка СБП (без параметра суммы)
        amount: Сумма в копейках (1 рубль = 100 копеек)
        parameter_name: Название параметра суммы ('sum', 'amount', и т.д.)

    Returns:
        URL с добавленным параметром суммы

    Example:
        >>> build_payment_url_with_amount(
        ...     "https://qr.nspk.ru/ABC123?type=01&bank=100000000261&crc=FDD5",
        ...     50000,  # 500 рублей
        ...     "sum"
        ... )
        "https://qr.nspk.ru/ABC123?type=01&bank=100000000261&sum=50000&crc=FDD5"
    """

    # Парсим URL
    parsed = urlparse(base_url)
    query_params = parse_qs(parsed.query, keep_blank_values=True)

    # Добавляем или обновляем параметр суммы
    query_params[parameter_name] = [str(amount)]

    # Собираем URL обратно
    new_query = urlencode(query_params, doseq=True)
    new_url = urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        new_query,
        parsed.fragment
    ))

    return new_url


def rubles_to_kopecks(rubles: float) -> int:
    """
    Конвертировать рубли в копейки.

    Args:
        rubles: Сумма в рублях (может быть с копейками, например 123.45)

    Returns:
        Сумма в копейках (целое число)

    Example:
        >>> rubles_to_kopecks(500.50)
        50050
    """
    return int(round(rubles * 100))


def kopecks_to_rubles(kopecks: int) -> float:
    """
    Конвертировать копейки в рубли.

    Args:
        kopecks: Сумма в копейках

    Returns:
        Сумма в рублях

    Example:
        >>> kopecks_to_rubles(50050)
        500.50
    """
    return kopecks / 100


def is_working_hours(db: Session, moscow_tz) -> tuple[bool, Optional[str]]:
    """
    Проверить, находимся ли мы в рабочее время.
    Возвращает (is_working, message)
    """
    now = datetime.now(moscow_tz)

    working_config = crud.get_working_hours_by_day(db, now.weekday())

    if not working_config or not working_config.is_enabled:
        return False, f"Сегодня ({get_day_name(now.weekday())}) не рабочий день"

    # Преобразуем строки времени в time объекты
    try:
        work_start = datetime.strptime(working_config.work_start, "%H:%M").time()
        work_end = datetime.strptime(working_config.work_end, "%H:%M").time()
    except ValueError:
        return False, "Ошибка в конфигурации рабочего времени"

    current_time = now.time()

    if work_start <= current_time <= work_end:
        return True, None
    else:
        return False, f"Рабочее время: {working_config.work_start} - {working_config.work_end}"


def get_day_name(day_of_week: int) -> str:
    """Получить название дня недели"""
    days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
    return days[day_of_week] if 0 <= day_of_week <= 6 else "Неизвестно"


def get_day_name_short(day_of_week: int) -> str:
    """Получить короткое название дня недели"""
    days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    return days[day_of_week] if 0 <= day_of_week <= 6 else "?"


def generate_qr_code(url: str, size: int = 280) -> str:
    """
    Генерировать QR код и вернуть как base64.

    Args:
        url: URL для кодирования
        size: Размер QR кода в пикселях

    Returns:
        Base64 строка изображения QR кода
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Конвертируем в base64
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)

    return base64.b64encode(img_io.getvalue()).decode()


def get_client_ip(request) -> str:
    """Получить IP клиента с учётом прокси"""
    if "x-forwarded-for" in request.headers:
        return request.headers["x-forwarded-for"].split(",")[0].strip()
    elif "x-real-ip" in request.headers:
        return request.headers["x-real-ip"]
    else:
        return request.client.host
