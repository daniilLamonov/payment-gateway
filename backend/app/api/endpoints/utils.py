from fastapi import APIRouter

from ...config import settings

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check эндпоинт"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }