from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any

class DynamicPaymentURLCreate(BaseModel):
    target_url: str = Field(..., min_length=10, max_length=500)
    valid_from: datetime
    valid_until: datetime
    notes: Optional[str] = None


class DynamicPaymentURLResponse(BaseModel):
    id: int
    target_url: str
    valid_from: datetime
    valid_until: datetime
    is_active: bool
    created_at: datetime
    notes: Optional[str] = None

    class Config:
        from_attributes = True

class APIResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    data: Optional[Any] = None


class QRCodeResponse(BaseModel):
    success: bool
    qr_code: Dict[str, Any]
    message: str
