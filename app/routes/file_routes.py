from app.schemas.file_schema import FileResponse
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
import shutil
import os

from app.database.database import get_db
from app.models.file import File as FileModel
from app.models.user import User
from app.security.auth import get_current_user
from fastapi.responses import FileResponse as FastAPIFileResponse
from app.schemas.file_schema import RenameFile
from fastapi import Query
from sqlalchemy import asc, desc
from app.security.encryption import encrypt_file
from fastapi.responses import Response
from app.security.encryption import decrypt_file
from app.services.activity_service import log_activity

router = APIRouter()


@router.post("/upload")
async def upload_file(
    folder_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    from app.models.folder import Folder

    folder = db.query(Folder).filter(
        Folder.id == folder_id,
        Folder.owner_id == current_user.id
    ).first()

    if folder is None:
        raise HTTPException(
            status_code=404,
            detail="Folder not found"
        )

    existing_versions = db.query(FileModel).filter(
        FileModel.owner_id == current_user.id,
        FileModel.folder_id == folder.id,
        FileModel.original_filename == file.filename
    ).count()

    version = existing_versions + 1

    name, extension = os.path.splitext(file.filename)

    stored_filename = f"{name}_v{version}{extension}"

    upload_folder = os.path.join(
        "uploads",
        current_user.username,
        folder.folder_name
    )

    os.makedirs(upload_folder, exist_ok=True)

    file_path = os.path.join(
        upload_folder,
        stored_filename
    )

    file_data = await file.read()

    encrypted_data = encrypt_file(file_data)

    with open(file_path, "wb") as buffer:
        buffer.write(encrypted_data)

    new_file = FileModel(
        filename=stored_filename,
        original_filename=file.filename,
        version=version,
        filepath=file_path,
        owner_id=current_user.id,
        folder_id=folder.id
    )

    db.add(new_file)
    db.commit()
    db.refresh(new_file)

    log_activity(
        db=db,
        user_id=current_user.id,
        action="FILE_UPLOADED",
        resource_type="FILE",
        resource_id=new_file.id,
        description=f"{stored_filename} uploaded to {folder.folder_name}",
        status="SUCCESS"
    )

    return {
        "message": "File uploaded successfully",
        "original_filename": new_file.original_filename,
        "stored_filename": new_file.filename,
        "version": new_file.version,
        "folder": folder.folder_name
    }
@router.get("/files", response_model=list[FileResponse])
def get_my_files(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    files = db.query(FileModel).filter(
        FileModel.owner_id == current_user.id
    ).all()

    return files
@router.get("/download/{file_id}")
def download_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    file = db.query(FileModel).filter(
        FileModel.id == file_id,
        FileModel.owner_id == current_user.id
    ).first()

    if file is None:
        raise HTTPException(
            status_code=404,
            detail="File not found"
        )

    if not os.path.exists(file.filepath):
        raise HTTPException(
            status_code=404,
            detail="Stored file not found"
        )

    with open(file.filepath, "rb") as f:
        encrypted_data = f.read()

    try:
        decrypted_data = decrypt_file(encrypted_data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    log_activity(
        db=db,
        user_id=current_user.id,
        action="FILE_DOWNLOADED",
        resource_type="FILE",
        resource_id=file.id,
        description=f"{file.filename} downloaded",
        status="SUCCESS"
    )

    return Response(
        content=decrypted_data,
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f'attachment; filename="{file.filename}"'
        }
    )
@router.put("/rename/{file_id}")
def rename_file(
    file_id: int,
    rename: RenameFile,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    file = db.query(FileModel).filter(
        FileModel.id == file_id
    ).first()

    if file is None:
        raise HTTPException(
            status_code=404,
            detail="File not found"
        )

    if file.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )

    old_path = file.filepath

    extension = os.path.splitext(old_path)[1]

    new_name = rename.new_filename + extension

    new_path = os.path.join(
        "uploads",
        new_name
    )

    if os.path.exists(new_path):
        raise HTTPException(
            status_code=400,
            detail="Filename already exists"
        )

    os.rename(old_path, new_path)

    file.filename = new_name
    file.filepath = new_path

    db.commit()
    db.refresh(file)

    return {
        "message": "File renamed successfully",
        "filename": file.filename
    }
@router.delete("/delete/{file_id}")
def delete_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    file = db.query(FileModel).filter(
        FileModel.id == file_id
    ).first()

    if file is None:
        raise HTTPException(
            status_code=404,
            detail="File not found"
        )

    if file.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )

    if os.path.exists(file.filepath):
        os.remove(file.filepath)

    log_activity(
        db=db,
        user_id=current_user.id,
        action="FILE_DELETED",
        resource_type="FILE",
        resource_id=file.id,
        description=f"{file.filename} deleted",
        status="SUCCESS"
    )

    db.delete(file)
    db.commit()

    return {
        "message": "File deleted successfully"
    }
@router.get("/search")
def search_files(
    filename: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    files = db.query(FileModel).filter(
        FileModel.owner_id == current_user.id,
        FileModel.filename.ilike(f"%{filename}%")
    ).all()

    return files
@router.get("/filter")
def filter_files(
    extension: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    files = db.query(FileModel).filter(
        FileModel.owner_id == current_user.id,
        FileModel.filename.ilike(f"%.{extension}")
    ).all()

    return files
@router.get("/sort")
def sort_files(
    order: str = "asc",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    query = db.query(FileModel).filter(
        FileModel.owner_id == current_user.id
    )

    if order.lower() == "desc":
        files = query.order_by(desc(FileModel.uploaded_at)).all()
    else:
        files = query.order_by(asc(FileModel.uploaded_at)).all()

    return files

@router.get("/versions/{file_id}")
def get_file_versions(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    file = db.query(FileModel).filter(
        FileModel.id == file_id,
        FileModel.owner_id == current_user.id
    ).first()

    if file is None:
        raise HTTPException(
            status_code=404,
            detail="File not found"
        )

    versions = db.query(FileModel).filter(
        FileModel.owner_id == current_user.id,
        FileModel.folder_id == file.folder_id,
        FileModel.original_filename == file.original_filename
    ).order_by(
        FileModel.version.desc()
    ).all()

    result = []

    for version in versions:

        result.append({

            "id": version.id,

            "original_filename": version.original_filename,

            "stored_filename": version.filename,

            "version": version.version,

            "uploaded_at": version.uploaded_at

        })

    return result

@router.get("/download-version/{version_id}")
def download_version(
    version_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    file = db.query(FileModel).filter(
        FileModel.id == version_id,
        FileModel.owner_id == current_user.id
    ).first()

    if file is None:
        raise HTTPException(
            status_code=404,
            detail="Version not found"
        )

    if not os.path.exists(file.filepath):
        raise HTTPException(
            status_code=404,
            detail="Stored file not found"
        )

    with open(file.filepath, "rb") as f:
        encrypted_data = f.read()

    try:
        decrypted_data = decrypt_file(encrypted_data)
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Encrypted file is corrupted"
        )

    log_activity(
        db=db,
        user_id=current_user.id,
        action="FILE_VERSION_DOWNLOADED",
        resource_type="FILE",
        resource_id=file.id,
        description=f"{file.filename} (Version {file.version}) downloaded",
        status="SUCCESS"
    )

    return Response(
        content=decrypted_data,
        media_type="application/octet-stream",
        headers={
            "Content-Disposition":
            f'attachment; filename="{file.original_filename}"'
        }
    )