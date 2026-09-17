from pydantic import BaseModel
from datetime import datetime


class ShareRequest(BaseModel):

    file_id: int

    shared_with: int

    permission: str

    expiry_date: datetime | None = None

    download_limit: int = 0

class SharedFileResponse(BaseModel):

    share_id: int

    file_id: int

    filename: str

    owner: str

    permission: str

    expiry_date: datetime | None

    download_limit: int

    download_count: int

    class Config:
        from_attributes = True


from pydantic import BaseModel
from datetime import datetime


class EditShareRequest(BaseModel):
    permission: str
    expiry_date: datetime | None = None
    download_limit: int = 0