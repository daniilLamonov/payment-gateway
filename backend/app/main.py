from fastapi import FastAPI, Depends
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
from urllib.parse import quote
import time

from . import models, crud, utils, config
from .database import engine, get_db
from .config import settings
from .api import router as api_router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)

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

@app.get("/pay/{payment_id}")
async def payment_gateway_tracked(payment_id: str, db: Session = Depends(get_db)):
    try:
        is_working, message = utils.is_working_hours(db, config.MOSCOW_TZ)

        if not is_working:
            return RedirectResponse(
                url=f"{settings.FRONTEND_URL}/payment-error?type=closed&message={quote(message)}",
                status_code=307
            )

        dynamic_url = crud.get_active_dynamic_url(db)

        if not dynamic_url:
            return RedirectResponse(
                url=f"{settings.FRONTEND_URL}/payment-error?type=maintenance",
                status_code=307
            )

        return RedirectResponse(
            url=dynamic_url.target_url,
            status_code=307
        )

    except Exception as e:
        print(f"❌ Error in payment_gateway: {str(e)}")
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/payment-error?type=error&message={quote(str(e))}",
            status_code=307
        )
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }