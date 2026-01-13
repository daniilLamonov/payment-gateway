from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import uuid

from ... import crud, utils, config
from ...database import get_db
from ...config import settings

router = APIRouter(tags=["payment"])

@router.get("/generate-qr")
async def generate_qr():
    try:
        session_id = str(uuid.uuid4())
        url = f"{settings.PROTOCOL}://{settings.DOMAIN}/pay/{session_id}"

        return {
            "success": True,
            "qr_code": {
                "url": url,
                "session_id": session_id
            },
            "message": "QR код сгенерирован"
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }

@router.get("/payment-link")
async def get_payment_link():
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
        return {
            "success": False,
            "message": str(e)
        }

@router.get("/payment-status")
async def check_payment_status(db: Session = Depends(get_db)):
    try:
        is_working, message = utils.is_working_hours(db, config.MOSCOW_TZ)

        if not is_working:
            return {
                "available": False,
                "reason": "closed",
                "message": message
            }

        dynamic_url = crud.get_active_dynamic_url(db)

        if not dynamic_url:
            return {
                "available": False,
                "reason": "maintenance",
                "message": "Платежная система временно недоступна"
            }

        return {
            "available": True,
            "message": "Платежная система доступна"
        }

    except Exception as e:
        print(f"❌ Error in payment-status: {str(e)}")
        return {
            "available": False,
            "reason": "error",
            "message": str(e)
        }
