from zoneinfo import ZoneInfo

from pydantic_settings import BaseSettings
from functools import lru_cache


MOSCOW_TZ = ZoneInfo("Europe/Moscow")


class Settings(BaseSettings):
    DEBUG: bool

    # CORS
    FRONTEND_URL: str

    # Domain
    DOMAIN: str
    PROTOCOL: str

    ADMIN_USERNAME: str
    ADMIN_PASSWORD: str

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    JWT_EXPIRATION_MINUTES: int

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
