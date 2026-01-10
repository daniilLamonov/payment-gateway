from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from .config import settings

# ============================================
# ХЕШИРОВАНИЕ ПАРОЛЕЙ
# ============================================
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверить пароль"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Получить хеш пароля"""
    return pwd_context.hash(password)


# ============================================
# JWT ТОКЕНЫ
# ============================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Создать JWT токен

    Args:
        data: Данные для кодирования в токен
        expires_delta: Время жизни токена

    Returns:
        JWT токен
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRATION_MINUTES)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    return encoded_jwt


def verify_token(token: str) -> dict:
    """
    Проверить JWT токен

    Args:
        token: JWT токен

    Returns:
        Декодированные данные из токена

    Raises:
        HTTPException: Если токен невалидный
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        username: str = payload.get("sub")

        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        return payload

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )


# ============================================
# АУТЕНТИФИКАЦИЯ ПОЛЬЗОВАТЕЛЯ
# ============================================

def authenticate_admin(username: str, password: str) -> bool:
    """
    Проверить учётные данные админа

    Args:
        username: Имя пользователя
        password: Пароль

    Returns:
        True если аутентификация успешна
    """
    # Проверяем username
    if username != settings.ADMIN_USERNAME:
        return False

    # Проверяем password
    # В продакшене храните хеш в .env, а не сам пароль!
    if password != settings.ADMIN_PASSWORD:
        return False

    return True


# ============================================
# DEPENDENCY ДЛЯ ЗАЩИЩЁННЫХ РОУТОВ
# ============================================

security = HTTPBearer()


async def get_current_admin(
        credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Dependency для защиты роутов.
    Проверяет JWT токен в заголовке Authorization.

    Usage:
        @app.get("/admin/something", dependencies=[Depends(get_current_admin)])
        async def protected_route():
            return {"message": "You are authenticated!"}
    """
    token = credentials.credentials
    payload = verify_token(token)
    return payload
