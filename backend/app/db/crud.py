from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime
from typing import Optional, List
from ..db import models
from ..api.schemas.payment_link import DynamicPaymentURLCreate
from ..api.schemas.workhours import WorkingHoursUpdate

def get_active_dynamic_url(db: Session) -> Optional[models.DynamicPaymentURL]:
    now = datetime.utcnow()
    return (
        db.query(models.DynamicPaymentURL)
        .filter(
            and_(
                models.DynamicPaymentURL.valid_from <= now,
                models.DynamicPaymentURL.valid_until >= now,
                models.DynamicPaymentURL.is_active == True,
            )
        )
        .first()
    )


def get_all_dynamic_urls(
    db: Session, limit: int = 100
) -> List[models.DynamicPaymentURL]:
    """Получить все динамические ссылки"""
    return (
        db.query(models.DynamicPaymentURL)
        .order_by(models.DynamicPaymentURL.created_at.desc())
        .limit(limit)
        .all()
    )


def create_dynamic_url(
    db: Session,
    url_data: DynamicPaymentURLCreate,
) -> models.DynamicPaymentURL:

    db.query(models.DynamicPaymentURL).update({"is_active": False})

    new_url = models.DynamicPaymentURL(
        target_url=url_data.target_url,
        valid_from=url_data.valid_from,
        valid_until=url_data.valid_until,
        is_active=True,
        notes=url_data.notes,
    )

    db.add(new_url)
    db.commit()
    db.refresh(new_url)

    return new_url


def get_working_hours_by_day(
    db: Session, day_of_week: int
) -> Optional[models.WorkingHours]:
    return (
        db.query(models.WorkingHours)
        .filter(models.WorkingHours.day_of_week == day_of_week)
        .first()
    )


def get_all_working_hours(db: Session) -> List[models.WorkingHours]:
    return db.query(models.WorkingHours).order_by(models.WorkingHours.day_of_week).all()


def update_or_create_working_hours(
    db: Session, hours_data: WorkingHoursUpdate
) -> models.WorkingHours:

    existing = get_working_hours_by_day(db, hours_data.day_of_week)

    if existing:
        existing.work_start = hours_data.work_start
        existing.work_end = hours_data.work_end
        existing.is_enabled = hours_data.is_enabled
        db.commit()
        db.refresh(existing)
        return existing
    else:
        new_hours = models.WorkingHours(
            day_of_week=hours_data.day_of_week,
            work_start=hours_data.work_start,
            work_end=hours_data.work_end,
            is_enabled=hours_data.is_enabled,
        )
        db.add(new_hours)
        db.commit()
        db.refresh(new_hours)
        return new_hours
