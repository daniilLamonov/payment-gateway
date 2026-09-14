from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Any

MAX_QR_IMAGE_BYTES = 2 * 1024 * 1024
ALLOWED_QR_IMAGE_TYPES = {"image/png", "image/jpeg", "image/webp", "image/gif"}


class DynamicPaymentURLCreate(BaseModel):
    name: str = ""
    target_url: Optional[str] = Field(default=None, max_length=500)
    valid_from: datetime
    valid_until: datetime


class DynamicPaymentURLResponse(BaseModel):
    id: int
    name: Optional[str] = None
    target_url: Optional[str] = None
    has_qr_image: bool = False
    qr_image_url: Optional[str] = None
    valid_from: datetime
    valid_until: datetime
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class APIResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    data: Optional[Any] = None
