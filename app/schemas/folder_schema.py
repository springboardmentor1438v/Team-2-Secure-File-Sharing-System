from pydantic import BaseModel


class FolderCreate(BaseModel):
    folder_name: str


class FolderResponse(BaseModel):
    id: int
    folder_name: str
    owner_id: int

    class Config:
        from_attributes = True