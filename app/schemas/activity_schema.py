from pydantic import BaseModel
from datetime import datetime


class ActivityResponse(BaseModel):
    id: int
    user_id: int | None
    action: str
    resource_type: str | None
    resource_id: int | None
    description: str | None
    status: str
    ip_address: str | None
    created_at: datetime

    class Config:
        from_attributes = True