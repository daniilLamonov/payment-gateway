from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, ForeignKey, Text
from sqlalchemy.sql import func
from .database import Base


class DynamicPaymentURL(Base):
    __tablename__ = "dynamic_payment_urls"

    id = Column(Integer, primary_key=True, index=True)
    target_url = Column(String(500), nullable=False)
    valid_from = Column(DateTime(timezone=True), nullable=False)
    valid_until = Column(DateTime(timezone=True), nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    notes = Column(Text, nullable=True)
    supports_amount = Column(Boolean, default=True)
    amount_parameter = Column(String(20), default="sum")


class WorkingHours(Base):
    __tablename__ = "working_hours"

    id = Column(Integer, primary_key=True, index=True)
    day_of_week = Column(Integer, index=True)
    work_start = Column(String(5))
    work_end = Column(String(5))
    is_enabled = Column(Boolean, default=True)
    timezone = Column(String(50), default="Europe/Moscow")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
