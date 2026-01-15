from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import OperationalError
import time

from .db import models
from .db.database import engine
from .core.config import settings
from .api import router as api_router

app = FastAPI(debug=settings.DEBUG)

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    max_retries = 10
    retry_interval = 2

    for attempt in range(max_retries):
        try:
            models.Base.metadata.create_all(bind=engine)
            break
        except OperationalError as e:
            if attempt < max_retries - 1:
                time.sleep(retry_interval)
            else:
                raise e


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }
