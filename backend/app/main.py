from datetime import timedelta

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
import uuid
import time

from starlette import status

from . import models, crud, utils, config
from .api.endpoints.html import render_not_working_hours_page, render_no_active_link_page, render_error_page
from .api.schemas.auth import LoginResponse, LoginRequest
from .api.schemas.payment_link import QRCodeResponse
from .auth import authenticate_admin, create_access_token, get_current_admin
from .database import engine, get_db
from .config import settings
from .api import router as api_router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)

app.include_router(api_router)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Bearer token scheme
security = HTTPBearer()



# ============================================
# STARTUP EVENT - создание таблиц при запуске
# ============================================

@app.on_event("startup")
async def startup_event():
    """
    Выполняется при запуске приложения.
    Создаёт таблицы в БД с retry логикой.
    """
    max_retries = 10
    retry_interval = 2  # секунды

    for attempt in range(max_retries):
        try:
            print(f"Попытка подключения к БД ({attempt + 1}/{max_retries})...")

            # Пробуем создать таблицы
            models.Base.metadata.create_all(bind=engine)

            print("✅ Успешно подключились к БД и создали таблицы!")
            break

        except OperationalError as e:
            if attempt < max_retries - 1:
                print(f"⚠️  Не удалось подключиться к БД. Повторная попытка через {retry_interval} секунд...")
                time.sleep(retry_interval)
            else:
                print(f"❌ Не удалось подключиться к БД после {max_retries} попыток!")
                raise e


@app.get("/pay/{mock}")
async def payment_gateway_tracked(db: Session = Depends(get_db)):

    try:
        # 1️⃣ Проверка рабочего времени
        is_working, message = utils.is_working_hours(db, config.MOSCOW_TZ)

        if not is_working:
            return await render_not_working_hours_page(db, message)

        # 2️⃣ Получение актуальной ссылки
        dynamic_url = crud.get_active_dynamic_url(db)

        if not dynamic_url:
            return await render_no_active_link_page()

        # 5️⃣ Редирект
        return RedirectResponse(
            url=dynamic_url.target_url,
            status_code=307
        )

    except Exception as e:
        print(f"Error in payment_gateway_tracked: {str(e)}")
        return await render_error_page(str(e))


# ============================================
# API - ГЕНЕРАЦИЯ QR
# ============================================

@app.get("/api/generate-qr", response_model=QRCodeResponse)
async def generate_qr(request: Request):
    """
    Генерирует QR коды для оплаты.

    Два варианта:
    1. Простой (без сессии): https://your-domain.com/pay
    2. С отслеживанием: https://your-domain.com/pay/{uuid}
    """

    try:
        session_id = str(uuid.uuid4())
        tracked_url = f"{settings.PROTOCOL}://{settings.DOMAIN}/pay/{session_id}"
        tracked_qr = utils.generate_qr_code(tracked_url)

        return {
            "success": True,
            "qr_code": {
                "url": tracked_url,
                "session_id": session_id,
                "qr": f"data:image/png;base64,{tracked_qr}",
            },
            "message": "QR код успешно сгенерирован"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/payment-link")
async def get_payment_link():
    """Получить ссылку на оплату"""

    try:
        session_id = str(uuid.uuid4())
        link = f"{settings.PROTOCOL}://{settings.DOMAIN}/pay/{session_id}"

        return {
            "success": True,
            "session_id": session_id,
            "link": link,
            "message": "Ссылка создана"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




@app.post("/api/auth/login", response_model=LoginResponse)
async def login(credentials: LoginRequest):
    """
    Логин для админа

    Принимает username и password, возвращает JWT токен.
    """

    # Проверяем учётные данные
    if not authenticate_admin(credentials.username, credentials.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Создаём JWT токен
    access_token_expires = timedelta(minutes=settings.JWT_EXPIRATION_MINUTES)
    access_token = create_access_token(
        data={"sub": credentials.username},
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": credentials.username
    }


@app.get("/api/auth/verify")
async def verify_auth(current_admin: dict = Depends(get_current_admin)):
    """
    Проверка валидности токена

    Используется фронтендом для проверки что пользователь всё ещё залогинен.
    """
    return {
        "authenticated": True,
        "username": current_admin.get("sub")
    }


@app.post("/api/auth/logout")
async def logout():
    """
    Логаут (на самом деле ничего не делает, т.к. JWT stateless)

    Фронтенд просто удаляет токен из localStorage.
    """
    return {"message": "Logged out successfully"}