from datetime import datetime

from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse

from ... import crud, config


async def render_not_working_hours_page(db: Session):
    """Страница вне рабочего времени"""

    now = datetime.now(config.MOSCOW_TZ)

    # Получаем рабочее время на сегодня
    today_hours = crud.get_working_hours_by_day(db, now.weekday())
    hours_text = f"{today_hours.work_start} - {today_hours.work_end}" if today_hours else "уточняйте позже"

    html = f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Платежная система закрыта</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }}
            .container {{
                background: white;
                border-radius: 16px;
                padding: 50px 40px;
                max-width: 500px;
                text-align: center;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            }}
            .icon {{ font-size: 80px; margin-bottom: 20px; }}
            h1 {{ font-size: 28px; color: #333; margin-bottom: 15px; }}
            .message {{ color: #666; font-size: 16px; line-height: 1.6; margin-bottom: 30px; }}
            .info-box {{
                background: #f0f7ff;
                border-left: 4px solid #667eea;
                padding: 20px;
                text-align: left;
                margin-bottom: 30px;
                border-radius: 8px;
            }}
            .info-box strong {{ color: #333; display: block; margin-bottom: 8px; }}
            .info-box p {{ color: #666; font-size: 15px; }}
            .button {{
                background: #667eea;
                color: white;
                border: none;
                padding: 14px 32px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: background 0.3s;
            }}
            .button:hover {{ background: #764ba2; }}
            .time {{ color: #999; font-size: 12px; margin-top: 20px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="icon">⏰</div>
            <h1>Платежная система закрыта</h1>

            <div class="info-box">
                <strong>Часы работы:</strong>
                <p>{hours_text} (МСК)</p>
            </div>

            <button class="button" onclick="location.reload()">
                ↻ Проверить позже
            </button>

            <div class="time">
                Сейчас: {now.strftime('%H:%M:%S')} МСК
            </div>
        </div>
    </body>
    </html>
    """

    return HTMLResponse(html)


async def render_no_active_link_page():
    """Страница когда нет активной ссылки"""

    html = """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Система платежей недоступна</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }
            .container {
                background: white;
                border-radius: 16px;
                padding: 50px 40px;
                max-width: 500px;
                text-align: center;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            }
            .icon { font-size: 80px; margin-bottom: 20px; }
            h1 { font-size: 28px; color: #f5576c; margin-bottom: 15px; }
            .message { color: #666; font-size: 16px; line-height: 1.6; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="icon">🔧</div>
            <h1>Система на техническом обслуживании</h1>
            <div class="message">
                Платежная система временно недоступна. Пожалуйста, попробуйте позже.
            </div>
        </div>
    </body>
    </html>
    """

    return HTMLResponse(html)


async def render_error_page(message: str):
    """Страница ошибки"""

    html = f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Ошибка</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }}
            .container {{
                background: white;
                border-radius: 16px;
                padding: 50px 40px;
                max-width: 500px;
                text-align: center;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            }}
            .icon {{ font-size: 80px; margin-bottom: 20px; }}
            h1 {{ font-size: 28px; color: #f5576c; margin-bottom: 15px; }}
            .message {{ color: #666; font-size: 16px; }}
            .button {{
                background: #f5576c;
                color: white;
                border: none;
                padding: 12px 30px;
                border-radius: 8px;
                cursor: pointer;
                margin-top: 20px;
                font-weight: 600;
            }}
            .button:hover {{ background: #f03957; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="icon">❌</div>
            <h1>Ошибка</h1>
            <div class="message">{message}</div>
            <button class="button" onclick="window.history.back()">← Назад</button>
        </div>
    </body>
    </html>
    """

    return HTMLResponse(html)