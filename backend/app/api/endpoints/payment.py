from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import uuid

from ...core import utils, config
from ...db import crud
from ...db.database import get_db

router = APIRouter(prefix="/api", tags=["payment"])


@router.get("/generate-qr")
async def generate_qr(db: Session = Depends(get_db)):
    try:
        is_working, message = utils.is_working_hours(db, config.MOSCOW_TZ)

        if not is_working:
            return {"success": False, "error": "closed", "message": message}

        dynamic_url = crud.get_active_dynamic_url(db)

        if not dynamic_url:
            return {
                "success": False,
                "error": "maintenance",
                "message": "Платежная система временно недоступна",
            }

        session_id = str(uuid.uuid4())
        url = dynamic_url.target_url

        return {
            "success": True,
            "qr_code": {"url": url, "session_id": session_id},
            "message": "QR код сгенерирован",
        }
    except Exception as e:
        return {"success": False, "error": "server_error", "message": str(e)}


@router.get("/payment-link")
async def get_payment_link(db: Session = Depends(get_db)):
    try:
        is_working, message = utils.is_working_hours(db, config.MOSCOW_TZ)

        if not is_working:
            return {"success": False, "error": "closed", "message": message}

        dynamic_url = crud.get_active_dynamic_url(db)

        if not dynamic_url:
            return {
                "success": False,
                "error": "maintenance",
                "message": "Платежная система временно недоступна",
            }

        session_id = str(uuid.uuid4())
        link = dynamic_url.target_url

        return {
            "success": True,
            "session_id": session_id,
            "link": link,
            "message": "Ссылка создана",
        }
    except Exception as e:
        return {"success": False, "error": "server_error", "message": str(e)}