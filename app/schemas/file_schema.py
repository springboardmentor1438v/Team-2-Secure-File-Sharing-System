from pydantic import BaseModel
from datetime import datetime


class FileResponse(BaseModel):
    id: int
    filename: str
    filepath: str
    uploaded_at: datetime
    owner_id: int
class RenameFile(BaseModel):
    new_filename: str

    class Config:
        from_attributes = True