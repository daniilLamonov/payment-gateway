from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...core import utils
from ...db import crud, models
from ...api.schemas.payment_link import (
    APIResponse,
    DynamicPaymentURLCreate,
    DynamicPaymentURLResponse,
)
from ...api.schemas.workhours import WorkingHoursUpdate, WorkingHoursResponse
from ...core.auth import get_current_admin
from ...core.config import settings, MOSCOW_TZ
from ...db.database import get_db

router = APIRouter(prefix="/admin", tags=["admin"])


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


@router.post("/dynamic-redirect", response_model=APIResponse)
async def update_dynamic_redirect(
        url_data: DynamicPaymentURLCreate,
        db: Session = Depends(get_db),
        current_admin: dict = Depends(get_current_admin),
):
    try:
        if url_data.valid_from >= url_data.valid_until:
            raise HTTPException(
                status_code=400, detail="valid_from must be before valid_until"
            )

        new_url = crud.create_dynamic_url(db, url_data)

        return {
            "success": True,
            "message": f"Динамический редирект обновлён! Действует с {url_data.valid_from} до {url_data.valid_until}",
            "data": {
                "id": new_url.id,
                "gateway_url": f"{settings.PROTOCOL}://{settings.DOMAIN}/pay",
                "target_url": new_url.target_url,
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
    return crud.get_all_dynamic_urls(db)


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
            "valid_from": dynamic_url.valid_from.isoformat(),
            "valid_until": dynamic_url.valid_until.isoformat(),
            "notes": dynamic_url.notes,
            "is_active": dynamic_url.is_active,
            "created_at": dynamic_url.created_at.isoformat() if hasattr(dynamic_url, 'created_at') else None
        },
    }