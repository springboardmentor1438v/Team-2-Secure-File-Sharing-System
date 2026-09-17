from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import Response
from datetime import datetime
import os

from app.security.encryption import decrypt_file

from app.database.database import get_db
from app.models.share import Share
from app.models.file import File
from app.models.user import User
from app.security.auth import get_current_user
from app.schemas.share_schema import ShareRequest, SharedFileResponse
from app.services.activity_service import log_activity
import mimetypes

router = APIRouter()



@router.post("/share")
def share_file(
    share: ShareRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    file = db.query(File).filter(
        File.id == share.file_id,
        File.owner_id == current_user.id
    ).first()

    if file is None:
        raise HTTPException(
            status_code=404,
            detail="File not found or you are not the owner"
        )

    recipient = db.query(User).filter(
        User.id == share.shared_with
    ).first()

    if recipient is None:
        raise HTTPException(
            status_code=404,
            detail="Recipient not found"
        )

    if recipient.id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="You cannot share a file with yourself"
        )

    new_share = Share(
        file_id=share.file_id,
        owner_id=current_user.id,
        shared_with=share.shared_with,
        permission=share.permission,
        expiry_date=share.expiry_date,
        download_limit=share.download_limit
    )

    db.add(new_share)
    db.commit()
    db.refresh(new_share)

    log_activity(
        db=db,
        user_id=current_user.id,
        action="FILE_SHARED",
        resource_type="SHARE",
        resource_id=new_share.id,
        description=f"Shared '{file.filename}' with {recipient.username}",
        status="SUCCESS"
    )

    return {
        "message": "File shared successfully",
        "share_id": new_share.id
    }
@router.get("/shared-with-me", response_model=list[SharedFileResponse])
def shared_with_me(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    shares = db.query(Share).filter(
        Share.shared_with == current_user.id,
        Share.is_revoked == False
    ).all()

    result = []

    for share in shares:

        file = db.query(File).filter(
            File.id == share.file_id
        ).first()

        owner = db.query(User).filter(
            User.id == share.owner_id
        ).first()

        result.append({

            "share_id": share.id,

            "file_id": file.id,

            "filename": file.filename,

            "owner": owner.username,

            "permission": share.permission,

            "expiry_date": share.expiry_date,

            "download_limit": share.download_limit,

            "download_count": share.download_count

        })

    return result
@router.get("/shared-download/{share_id}")
def shared_download(
    share_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    share = db.query(Share).filter(
        Share.id == share_id,
        Share.shared_with == current_user.id
    ).first()

    if share is None:

        log_activity(
            db=db,
            user_id=current_user.id,
            action="UNAUTHORIZED_ACCESS",
            resource_type="SHARE",
            resource_id=share_id,
            description=f"Unauthorized access attempt for share ID {share_id}",
            status="FAILED"
        )

        raise HTTPException(
            status_code=404,
            detail="Share not found"
        )

    if share.is_revoked:

        log_activity(
            db=db,
            user_id=current_user.id,
            action="UNAUTHORIZED_ACCESS",
            resource_type="SHARE",
            resource_id=share.id,
            description="Attempted to access a revoked share",
            status="FAILED"
        )

        raise HTTPException(
            status_code=403,
            detail="Share has been revoked"
        )

    if share.expiry_date and datetime.now() > share.expiry_date:

        log_activity(
            db=db,
            user_id=current_user.id,
            action="UNAUTHORIZED_ACCESS",
            resource_type="SHARE",
            resource_id=share.id,
            description="Attempted to access an expired share",
            status="FAILED"
        )

        raise HTTPException(
            status_code=403,
            detail="Share has expired"
        )

    if share.permission != "DOWNLOAD":

        log_activity(
            db=db,
            user_id=current_user.id,
            action="UNAUTHORIZED_ACCESS",
            resource_type="SHARE",
            resource_id=share.id,
            description="Download permission denied",
            status="FAILED"
        )

        raise HTTPException(
            status_code=403,
            detail="Download permission denied"
        )

    if (
        share.download_limit > 0 and
        share.download_count >= share.download_limit
    ):

        log_activity(
            db=db,
            user_id=current_user.id,
            action="UNAUTHORIZED_ACCESS",
            resource_type="SHARE",
            resource_id=share.id,
            description="Download limit reached",
            status="FAILED"
        )

        raise HTTPException(
            status_code=403,
            detail="Download limit reached"
        )

    file = db.query(File).filter(
        File.id == share.file_id
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
      print("Decrypt Error:", e)

      raise HTTPException(
        status_code=500,
        detail=str(e)
    )

    share.download_count += 1
    db.commit()

    log_activity(
        db=db,
        user_id=current_user.id,
        action="FILE_DOWNLOADED",
        resource_type="FILE",
        resource_id=file.id,
        description=f"{file.filename} downloaded through shared link",
        status="SUCCESS"
    )

    return Response(
        content=decrypted_data,
        media_type="application/octet-stream",
        headers={
            "Content-Disposition":
            f'attachment; filename="{file.filename}"'
        }
    )

# @router.put("/revoke/{share_id}")
# def revoke_share(
#     share_id: int,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     share = db.query(Share).filter(
#         Share.id == share_id,
#         Share.owner_id == current_user.id
#     ).first()

#     if share is None:
#         raise HTTPException(
#             status_code=404,
#             detail="Share not found"
#         )

#     if share.is_revoked:
#         raise HTTPException(
#             status_code=400,
#             detail="Share already revoked"
#         )

#     share.is_revoked = True

#     db.commit()

#     return {
#         "message": "Share revoked successfully"
#     }

@router.put("/revoke/{share_id}")
def revoke_share(
    share_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    share = db.query(Share).filter(
        Share.id == share_id,
        Share.owner_id == current_user.id
    ).first()

    if share is None:
        raise HTTPException(
            status_code=404,
            detail="Share not found"
        )

    if share.is_revoked:
        raise HTTPException(
            status_code=400,
            detail="Share already revoked"
        )

    share.is_revoked = True

    db.commit()
    db.refresh(share)

    log_activity(
        db=db,
        user_id=current_user.id,
        action="SHARE_REVOKED",
        resource_type="SHARE",
        resource_id=share.id,
        description=f"Revoked share ID {share.id}",
        status="SUCCESS"
    )

    return {
        "message": "Share revoked successfully"
    }
@router.get("/shared-view/{share_id}")
def shared_view(
    share_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    share = db.query(Share).filter(
        Share.id == share_id,
        Share.shared_with == current_user.id
    ).first()

    if share is None:
        raise HTTPException(
            status_code=404,
            detail="Share not found"
        )

    if share.is_revoked:
        raise HTTPException(
            status_code=403,
            detail="Share has been revoked"
        )

    if share.expiry_date and datetime.now() > share.expiry_date:
        raise HTTPException(
            status_code=403,
            detail="Share has expired"
        )

    file = db.query(File).filter(
        File.id == share.file_id
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

        print("Decrypt Error:", e)

        raise HTTPException(
            status_code=500,
            detail="Encrypted file is corrupted"
        )

    mime_type, _ = mimetypes.guess_type(file.filename)

    if mime_type is None:
        mime_type = "application/octet-stream"

    log_activity(
        db=db,
        user_id=current_user.id,
        action="FILE_VIEWED",
        resource_type="FILE",
        resource_id=file.id,
        description=f"{file.filename} viewed",
        status="SUCCESS"
    )

    return Response(
        content=decrypted_data,
        media_type=mime_type,
        headers={
            "Content-Disposition": f'inline; filename="{file.filename}"'
        }
    )

@router.get("/my-shares")
def my_shares(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    shares = (
        db.query(Share)
        .filter(Share.owner_id == current_user.id)
        .all()
    )

    result = []

    for share in shares:

        file = db.query(File).filter(
            File.id == share.file_id
        ).first()

        recipient = db.query(User).filter(
            User.id == share.shared_with
        ).first()

        result.append({
            "share_id": share.id,
            "file_id": share.file_id,
            "filename": file.filename if file else "Deleted File",
            "shared_with": recipient.username if recipient else "Unknown User",
            "permission": share.permission,
            "expiry_date": share.expiry_date,
            "download_limit": share.download_limit,
            "download_count": share.download_count,
            "is_revoked": share.is_revoked
        })

    return result
from app.schemas.share_schema import (
    ShareRequest,
    SharedFileResponse,
    EditShareRequest
)

@router.put("/edit-share/{share_id}")
def edit_share(
    share_id: int,
    request: EditShareRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    existing_share = db.query(Share).filter(
        Share.id == share_id,
        Share.owner_id == current_user.id
    ).first()

    if existing_share is None:
        raise HTTPException(
            status_code=404,
            detail="Share not found"
        )

    if existing_share.is_revoked:
        raise HTTPException(
            status_code=400,
            detail="Cannot edit a revoked share"
        )

    if request.permission not in ["VIEW", "DOWNLOAD"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid permission"
        )

    if request.download_limit < 0:
        raise HTTPException(
            status_code=400,
            detail="Download limit cannot be negative"
        )

    existing_share.permission = request.permission
    existing_share.expiry_date = request.expiry_date
    existing_share.download_limit = request.download_limit

    db.commit()
    db.refresh(existing_share)

    log_activity(
        db=db,
        user_id=current_user.id,
        action="SHARE_UPDATED",
        resource_type="SHARE",
        resource_id=existing_share.id,
        description=f"Updated sharing settings for share ID {existing_share.id}",
        status="SUCCESS"
    )

    return {
        "message": "Share updated successfully"
    }