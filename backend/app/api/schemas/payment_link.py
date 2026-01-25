from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Any


class DynamicPaymentURLCreate(BaseModel):
    name: str
    target_url: str = Field(..., min_length=10, max_length=500)
    valid_from: datetime
    valid_until: datetime

class DynamicPaymentURLResponse(BaseModel):
    id: int
    name: str
    target_url: str
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
