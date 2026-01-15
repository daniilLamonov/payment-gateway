from pydantic import BaseModel, Field


class WorkingHoursUpdate(BaseModel):
    day_of_week: int = Field(..., ge=0, le=6)
    work_start: str = Field(..., pattern=r"^\d{2}:\d{2}$")
    work_end: str = Field(..., pattern=r"^\d{2}:\d{2}$")
    is_enabled: bool = True


class WorkingHoursResponse(BaseModel):
    id: int
    day_of_week: int
    work_start: str
    work_end: str
    is_enabled: bool

    class Config:
        from_attributes = True
