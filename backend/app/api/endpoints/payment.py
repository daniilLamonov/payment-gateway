from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
import uuid

from ...core import utils, config
from ...db import crud, models
from ...db.database import get_db

router = APIRouter(prefix="/api", tags=["payment"])


def _qr_image_url(dynamic_url: models.DynamicPaymentURL) -> str | None:
    return f"/api/qr-image/{dynamic_url.id}" if dynamic_url.qr_image else None


def _active_url_or_error(db: Session):
    """Вернуть активную ссылку либо словарь с причиной отказа."""
    is_working, message = utils.is_working_hours(db, config.MOSCOW_TZ)

    if not is_working:
        return None, {"success": False, "error": "closed", "message": message}

    dynamic_url = crud.get_active_dynamic_url(db)

    if not dynamic_url:
        return None, {
            "success": False,
            "error": "maintenance",
            "message": "Платежная система временно недоступна",
        }

    return dynamic_url, None


@router.get("/generate-qr")
async def generate_qr(db: Session = Depends(get_db)):
    try:
        dynamic_url, error = _active_url_or_error(db)
        if error:
            return error

        return {
            "success": True,
            "qr_code": {
                "url": dynamic_url.target_url,
                "image_url": _qr_image_url(dynamic_url),
                "session_id": str(uuid.uuid4()),
            },
            "message": "QR код сгенерирован",
        }
    except Exception as e:
        return {"success": False, "error": "server_error", "message": str(e)}


@router.get("/payment-link")
async def get_payment_link(db: Session = Depends(get_db)):
    try:
        dynamic_url, error = _active_url_or_error(db)
        if error:
            return error

        return {
            "success": True,
            "session_id": str(uuid.uuid4()),
            "link": dynamic_url.target_url,
            "qr_image_url": _qr_image_url(dynamic_url),
            "message": "Ссылка создана",
        }
    except Exception as e:
        return {"success": False, "error": "server_error", "message": str(e)}


@router.get("/qr-image/{redirect_id}")
async def get_qr_image(redirect_id: int, db: Session = Depends(get_db)):
    """Отдать загруженную админом картинку QR-кода. Публичный доступ: её видит плательщик."""
    dynamic_url = (
        db.query(models.DynamicPaymentURL)
        .filter(models.DynamicPaymentURL.id == redirect_id)
        .first()
    )

    if not dynamic_url or not dynamic_url.qr_image:
        raise HTTPException(status_code=404, detail="QR-код не найден")

    return Response(
        content=dynamic_url.qr_image,
        media_type=dynamic_url.qr_image_type or "image/png",
        headers={"Cache-Control": "public, max-age=300"},
    )
