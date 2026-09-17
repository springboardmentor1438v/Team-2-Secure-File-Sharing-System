from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.folder import Folder
from app.models.user import User
from app.schemas.folder_schema import FolderCreate, FolderResponse
from app.security.auth import get_current_user
from typing import List

router = APIRouter()


@router.post("/folders", response_model=FolderResponse)
def create_folder(
    folder: FolderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    existing_folder = db.query(Folder).filter(
        Folder.folder_name == folder.folder_name,
        Folder.owner_id == current_user.id
    ).first()

    if existing_folder:
        raise HTTPException(
            status_code=400,
            detail="Folder already exists"
        )

    new_folder = Folder(
        folder_name=folder.folder_name,
        owner_id=current_user.id
    )

    db.add(new_folder)
    db.commit()
    db.refresh(new_folder)

    return new_folder
@router.get("/folders", response_model=list[FolderResponse])
def get_folders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    folders = db.query(Folder).filter(
        Folder.owner_id == current_user.id
    ).all()

    return folders


from app.models.file import File as FileModel

@router.put("/folders/{folder_id}", response_model=FolderResponse)
def rename_folder(
    folder_id: int,
    folder: FolderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Find the folder belonging to the logged-in user
    existing_folder = db.query(Folder).filter(
        Folder.id == folder_id,
        Folder.owner_id == current_user.id
    ).first()

    if existing_folder is None:
        raise HTTPException(
            status_code=404,
            detail="Folder not found"
        )

    # Check if another folder with the new name already exists
    duplicate_folder = db.query(Folder).filter(
        Folder.folder_name == folder.folder_name,
        Folder.owner_id == current_user.id,
        Folder.id != folder_id
    ).first()

    if duplicate_folder:
        raise HTTPException(
            status_code=400,
            detail="A folder with this name already exists"
        )

    # Rename folder
    existing_folder.folder_name = folder.folder_name

    db.commit()
    db.refresh(existing_folder)

    return existing_folder

@router.delete("/folders/{folder_id}")
def delete_folder(
    folder_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    folder = db.query(Folder).filter(
        Folder.id == folder_id,
        Folder.owner_id == current_user.id
    ).first()

    if folder is None:
        raise HTTPException(
            status_code=404,
            detail="Folder not found"
        )

    files = db.query(FileModel).filter(
        FileModel.folder_id == folder.id
    ).first()

    if files:
        raise HTTPException(
            status_code=400,
            detail="Folder is not empty. Delete all files first."
        )

    db.delete(folder)
    db.commit()

    return {
        "message": "Folder deleted successfully"
    }