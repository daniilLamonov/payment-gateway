from zoneinfo import ZoneInfo

from pydantic_settings import BaseSettings
from functools import lru_cache


MOSCOW_TZ = ZoneInfo("Europe/Moscow")

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Payment Gateway"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # CORS
    FRONTEND_URL: str = "http://localhost:3000"

    # Domain
    DOMAIN: str = "localhost:8000"
    PROTOCOL: str = "http"

    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin123"  # ИЗМЕНИТЕ НА СВОЙ!

    # JWT Secret Key (сгенерируйте свой: openssl rand -hex 32)
    JWT_SECRET_KEY: str = "your-secret-key-change-me-in-production-please-use-openssl-rand-hex-32"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 60 * 24  # 24 часа

    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()
