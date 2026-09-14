from datetime import datetime
from io import BytesIO
from typing import List, Optional
from urllib.parse import urlparse

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError
from sqlalchemy.orm import Session

from ...core import utils
from ...db import crud, models
from ...api.schemas.payment_link import (
    ALLOWED_QR_IMAGE_TYPES,
    MAX_QR_IMAGE_BYTES,
    APIResponse,
    DynamicPaymentURLCreate,
    DynamicPaymentURLResponse,
)
from ...api.schemas.workhours import WorkingHoursUpdate, WorkingHoursResponse
from ...core.auth import get_current_admin
from ...core.config import settings, MOSCOW_TZ
from ...db.database import get_db

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.put("/working-hours", response_model=APIResponse)
async def update_working_hours(
        hours_data: WorkingHoursUpdate,
        db: Session = Depends(get_db),
        current_admin: dict = Depends(get_current_admin)
):

    try:
        datetime.strptime(hours_data.work_start, "%H:%M")
        datetime.strptime(hours_data.work_end, "%H:%M")

        updated_hours = crud.update_or_create_working_hours(db, hours_data)

        return {
            "success": True,
            "message": f"Рабочее время для {utils.get_day_name(hours_data.day_of_week)} обновлено: {hours_data.work_start} - {hours_data.work_end}",
            "data": {
                "day_of_week": updated_hours.day_of_week,
                "work_start": updated_hours.work_start,
                "work_end": updated_hours.work_end,
            },
        }

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid time format. Use HH:MM")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/working-hours", response_model=List[WorkingHoursResponse])
async def get_all_working_hours(
    db: Session = Depends(get_db), current_admin: dict = Depends(get_current_admin)
):
    return crud.get_all_working_hours(db)


def _clean_target_url(raw: Optional[str]) -> Optional[str]:
    """Привести ссылку к виду, пригодному для редиректа, или отвергнуть с понятным текстом."""
    if raw is None:
        return None

    url = raw.strip()
    if not url:
        return None

    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise HTTPException(
            status_code=400,
            detail="Ссылка должна начинаться с http:// или https:// и содержать адрес сайта. "
                   "Например: https://qr.nspk.ru/AS100...",
        )
    if len(url) > 500:
        raise HTTPException(
            status_code=400, detail="Ссылка слишком длинная (максимум 500 символов)"
        )
    return url


async def _read_qr_image(upload: Optional[UploadFile]) -> tuple[Optional[bytes], Optional[str]]:
    """Прочитать и проверить загруженную картинку QR-кода."""
    if upload is None or not upload.filename:
        return None, None

    content = await upload.read()

    if not content:
        raise HTTPException(status_code=400, detail="Файл QR-кода пустой")

    if len(content) > MAX_QR_IMAGE_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"Файл слишком большой ({len(content) // 1024} КБ). "
                   f"Максимум {MAX_QR_IMAGE_BYTES // 1024} КБ",
        )

    content_type = (upload.content_type or "").lower()
    if content_type not in ALLOWED_QR_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Поддерживаются только изображения PNG, JPEG, WebP или GIF",
        )

    try:
        Image.open(BytesIO(content)).verify()
    except (UnidentifiedImageError, OSError):
        raise HTTPException(
            status_code=400, detail="Не удалось прочитать изображение — файл повреждён"
        )

    return content, content_type


@router.post("/dynamic-redirect", response_model=APIResponse)
async def update_dynamic_redirect(
        valid_from: datetime = Form(...),
        valid_until: datetime = Form(...),
        name: str = Form(""),
        target_url: Optional[str] = Form(None),
        qr_image: Optional[UploadFile] = File(None),
        db: Session = Depends(get_db),
        current_admin: dict = Depends(get_current_admin),
):
    try:
        if valid_from >= valid_until:
            raise HTTPException(
                status_code=400,
                detail="Дата начала должна быть раньше даты окончания",
            )

        clean_url = _clean_target_url(target_url)
        image_bytes, image_type = await _read_qr_image(qr_image)

        if not clean_url and not image_bytes:
            raise HTTPException(
                status_code=400,
                detail="Укажите ссылку на оплату или загрузите изображение QR-кода "
                       "(можно и то, и другое)",
            )

        url_data = DynamicPaymentURLCreate(
            name=name,
            target_url=clean_url,
            valid_from=valid_from,
            valid_until=valid_until,
        )

        new_url = crud.create_dynamic_url(db, url_data, image_bytes, image_type)

        if clean_url and image_bytes:
            what = "Ссылка и QR-код сохранены"
        elif image_bytes:
            what = "QR-код сохранён"
        else:
            what = "Ссылка сохранена"

        return {
            "success": True,
            "message": f"{what}. Действует с {valid_from:%d.%m.%Y %H:%M} до {valid_until:%d.%m.%Y %H:%M}",
            "data": {
                "id": new_url.id,
                "gateway_url": f"{settings.PROTOCOL}://{settings.DOMAIN}/pay",
                "target_url": new_url.target_url,
                "qr_image_url": f"/api/qr-image/{new_url.id}" if image_bytes else None,
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/dynamic-redirect/{redirect_id}/toggle")
async def toggle_redirect_status(
        redirect_id: int,
        db: Session = Depends(get_db),
        current_admin: dict = Depends(get_current_admin)
):
    redirect = db.query(models.DynamicPaymentURL).filter(
        models.DynamicPaymentURL.id == redirect_id
    ).first()

    if not redirect:
        raise HTTPException(status_code=404, detail="Ссылка не найдена")

    now = datetime.now(MOSCOW_TZ)

    valid_from = redirect.valid_from
    valid_until = redirect.valid_until

    if valid_from.tzinfo is None:
        valid_from = valid_from.replace(tzinfo=MOSCOW_TZ)

    if valid_until.tzinfo is None:
        valid_until = valid_until.replace(tzinfo=MOSCOW_TZ)

    if redirect.is_active:
        redirect.is_active = False
        db.commit()
        db.refresh(redirect)

        return {
            "success": True,
            "message": "Ссылка деактивирована",
            "redirect": {
                "id": redirect.id,
                "is_active": redirect.is_active
            }
        }
    else:
        if now < valid_from:
            raise HTTPException(
                status_code=400,
                detail=f"Ссылка еще не действительна. Начало действия: {valid_from.strftime('%d.%m.%Y %H:%M')}"
            )

        if now > valid_until:
            raise HTTPException(
                status_code=400,
                detail=f"Срок действия ссылки истёк: {valid_until.strftime('%d.%m.%Y %H:%M')}"
            )

        db.query(models.DynamicPaymentURL).update({"is_active": False})

        redirect.is_active = True
        db.commit()
        db.refresh(redirect)

        return {
            "success": True,
            "message": "Ссылка активирована. Все другие ссылки деактивированы.",
            "redirect": {
                "id": redirect.id,
                "is_active": redirect.is_active
            }
        }


@router.get("/dynamic-redirects", response_model=List[DynamicPaymentURLResponse])
async def get_all_redirects(
        db: Session = Depends(get_db),
        current_admin: dict = Depends(get_current_admin)
):
    return [
        {
            "id": item.id,
            "name": item.name,
            "target_url": item.target_url,
            "has_qr_image": item.qr_image is not None,
            "qr_image_url": f"/api/qr-image/{item.id}" if item.qr_image else None,
            "valid_from": item.valid_from,
            "valid_until": item.valid_until,
            "is_active": item.is_active,
            "created_at": item.created_at,
        }
        for item in crud.get_all_dynamic_urls(db)
    ]


@router.get("/current-redirect")
async def get_current_redirect(
        db: Session = Depends(get_db),
        current_admin: dict = Depends(get_current_admin)
):
    dynamic_url = crud.get_active_dynamic_url(db)

    if not dynamic_url:
        return {"success": False, "error": "No active redirect configured"}

    return {
        "success": True,
        "redirect": {
            "id": dynamic_url.id,
            "gateway_url": f"{settings.PROTOCOL}://{settings.DOMAIN}/pay",
            "target_url": dynamic_url.target_url,
            "has_qr_image": dynamic_url.qr_image is not None,
            "qr_image_url": f"/api/qr-image/{dynamic_url.id}" if dynamic_url.qr_image else None,
            "valid_from": dynamic_url.valid_from.isoformat(),
            "valid_until": dynamic_url.valid_until.isoformat(),
            "name": dynamic_url.name,
            "is_active": dynamic_url.is_active,
            "created_at": dynamic_url.created_at.isoformat() if hasattr(dynamic_url, 'created_at') else None
        },
    }

@router.delete("/{redirect_id}")
async def delete_redirect(
        redirect_id: int,
        db: Session = Depends(get_db),
        current_admin: dict = Depends(get_current_admin)):
    redirect = crud.delete_dynamic_url(db, redirect_id)
    if not redirect:
        raise HTTPException(status_code=404, detail="redirect does not exist")
    return {"success": True}