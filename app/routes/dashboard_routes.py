from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
import os

from app.database.database import get_db
from app.models.activity_log import ActivityLog
from app.models.file import File
from app.models.share import Share
from app.models.user import User
from app.security.auth import get_current_user
from fastapi import HTTPException
from sqlalchemy import func
from app.models.user import User
from app.models.share import Share
from app.models.file import File
from app.services.activity_service import log_activity
from app.schemas.user_schema import ChangeRoleRequest
from app.models.folder import Folder




router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get("/all-users")
def all_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    users = db.query(User).all()

    result = []

    for user in users:
        result.append({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role
        })

    return result


@router.get("/active-users")
def active_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    users = (
        db.query(User)
        .join(
            ActivityLog,
            ActivityLog.user_id == User.id
        )
        .filter(
            ActivityLog.action == "LOGIN_SUCCESS"
        )
        .distinct(User.id)
        .all()
    )

    result = []

    for user in users:
        result.append({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role
        })

    return result


@router.get("/failed-logins")
def failed_logins(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    logs = (
        db.query(ActivityLog)
        .filter(
            ActivityLog.action == "LOGIN_FAILED"
        )
        .order_by(
            ActivityLog.created_at.desc()
        )
        .all()
    )

    return logs


@router.get("/security-events")
def security_events(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    logs = (
        db.query(ActivityLog)
        .filter(
            ActivityLog.action == "UNAUTHORIZED_ACCESS"
        )
        .order_by(
            ActivityLog.created_at.desc()
        )
        .all()
    )

    return logs


@router.get("/active-shares")
def active_shares(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    shares = (
        db.query(Share)
        .filter(
            Share.is_revoked == False
        )
        .all()
    )

    return shares


@router.get("/expired-shares")
def expired_shares(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    shares = (
        db.query(Share)
        .filter(
            Share.expiry_date != None,
            Share.expiry_date < datetime.now()
        )
        .all()
    )

    return shares


@router.get("/most-downloaded-files")
def most_downloaded_files(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    files = (
        db.query(File)
        .filter(File.owner_id == current_user.id)
        .all()
    )

    result = []

    for file in files:

        downloads = (
            db.query(func.count(ActivityLog.id))
            .filter(
                ActivityLog.action == "FILE_DOWNLOADED",
                ActivityLog.resource_id == file.id
            )
            .scalar()
        )

        result.append({
            "file_id": file.id,
            "filename": file.filename,
            "downloads": downloads
        })

    result.sort(
        key=lambda x: x["downloads"],
        reverse=True
    )

    return result[:5]

@router.get("/total-files")
def total_files(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    total = (
    db.query(func.count(File.id))
    .filter(File.owner_id == current_user.id)
    .scalar()
)

    return {
        "total_files": total
    }

@router.get("/storage-usage")
def storage_usage(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    

    files = (
    db.query(File)
    .filter(File.owner_id == current_user.id)
    .all()
)

    total_bytes = 0

    for file in files:
        if os.path.exists(file.filepath):
            total_bytes += os.path.getsize(file.filepath)

    if total_bytes < 1024:
        storage = f"{total_bytes} Bytes"
    elif total_bytes < 1024 * 1024:
        storage = f"{round(total_bytes / 1024, 2)} KB"
    elif total_bytes < 1024 * 1024 * 1024:
        storage = f"{round(total_bytes / (1024 * 1024), 2)} MB"
    else:
        storage = f"{round(total_bytes / (1024 * 1024 * 1024), 2)} GB"

    return {
        "storage_used": storage,
        "total_bytes": total_bytes
    }

@router.get("/shared-files-count")
def shared_files_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    total = (
        db.query(func.count(Share.id))
        .filter(
            Share.owner_id == current_user.id,
            Share.is_revoked == False
        )
        .scalar()
    )

    return {
        "shared_files": total
    }

@router.get("/recent-activity")
def recent_activity(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    

    activities = (
    db.query(ActivityLog)
    .filter(ActivityLog.user_id == current_user.id)
    .order_by(ActivityLog.created_at.desc())
    .limit(10)
    .all()
)

    result = []

    for activity in activities:
        result.append({
            "id": activity.id,
            "user_id": activity.user_id,
            "action": activity.action,
            "resource_type": activity.resource_type,
            "resource_id": activity.resource_id,
            "description": activity.description,
            "status": activity.status,
            "created_at": activity.created_at
        })

    return result

@router.get("/total-users")
def total_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )

    total = db.query(func.count(User.id)).scalar()

    return {
        "total_users": total
    }

@router.get("/admin/total-shares")
def total_shares(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )

    total = db.query(func.count(Share.id)).scalar()

    return {
        "total_shares": total
    }
@router.get("/admin/total-files")
def total_files_admin(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )

    total = db.query(func.count(File.id)).scalar()

    return {
        "total_files": total
    }
@router.get("/admin/active-shares")
def active_shares(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )

    total = db.query(func.count(Share.id)).filter(
        Share.is_revoked == False
    ).scalar()

    return {
        "active_shares": total
    }

@router.get("/all-files")
def get_all_files(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    files = db.query(File).all()

    result = []

    for file in files:

        owner = db.query(User).filter(
            User.id == file.owner_id
        ).first()

        result.append({

            "id": file.id,
            "filename": file.filename,
            "owner": owner.username if owner else "Unknown",
            "owner_id": file.owner_id,
            "filepath": file.filepath,
            "uploaded_at": file.uploaded_at

        })

    return result

@router.delete("/delete-file/{file_id}")
def delete_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    file = db.query(File).filter(
        File.id == file_id
    ).first()

    if file is None:
        raise HTTPException(
            status_code=404,
            detail="File not found"
        )

    # Delete physical file
    if os.path.exists(file.filepath):
        os.remove(file.filepath)

    # Delete all shares of this file
    db.query(Share).filter(
       Share.file_id == file_id
    ).delete()

    filename = file.filename

    db.delete(file)
    db.commit()

    log_activity(
        db=db,
        user_id=current_user.id,
        action="FILE_DELETED",
        resource_type="FILE",
        resource_id=file_id,
        description=f"Admin deleted {filename}",
        status="SUCCESS"
    )

    return {
        "message": "File deleted successfully"
    }

@router.put("/change-role/{user_id}")
def change_role(
    user_id: int,
    request: ChangeRoleRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if str(current_user.role).strip().upper() != "ADMIN":

        log_activity(
            db=db,
            user_id=current_user.id,
            action="UNAUTHORIZED_ACCESS",
            resource_type="ADMIN",
            resource_id=user_id,
            description=(
                f"{current_user.username} attempted to change "
                f"user role without admin permission"
            ),
            status="FAILED"
        )

        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    if current_user.id == user_id:

        raise HTTPException(
            status_code=400,
            detail="You cannot change your own role."
        )

    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if user is None:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    new_role = str(request.role).strip().upper()

    if new_role not in ["ADMIN", "USER"]:

        raise HTTPException(
            status_code=400,
            detail="Invalid role"
        )

    user.role = new_role

    db.commit()
    db.refresh(user)

    log_activity(
        db=db,
        user_id=current_user.id,
        action="ROLE_CHANGED",
        resource_type="USER",
        resource_id=user.id,
        description=(
            f"{current_user.username} changed "
            f"{user.username}'s role to {new_role}"
        ),
        status="SUCCESS"
    )

    return {
        "message": "Role updated successfully",
        "user_id": user.id,
        "username": user.username,
        "role": user.role
    }

@router.get("/shared-with-me-count")
def shared_with_me_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    total = (
        db.query(func.count(Share.id))
        .filter(
            Share.shared_with == current_user.id,
            Share.is_revoked == False
        )
        .scalar()
    )

    return {
        "shared_with_me": total
    }

@router.get("/admin/storage-usage")
def admin_storage_usage(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    files = db.query(File).all()

    total_bytes = 0

    for file in files:

        if os.path.exists(file.filepath):
            total_bytes += os.path.getsize(file.filepath)

    if total_bytes < 1024:

        storage = f"{total_bytes} Bytes"

    elif total_bytes < 1024 * 1024:

        storage = f"{round(total_bytes / 1024, 2)} KB"

    elif total_bytes < 1024 * 1024 * 1024:

        storage = f"{round(total_bytes / (1024 * 1024), 2)} MB"

    else:

        storage = f"{round(total_bytes / (1024 * 1024 * 1024), 2)} GB"

    return {
        "storage_used": storage,
        "total_bytes": total_bytes
    }

@router.get("/admin/download-activity")
def admin_download_activity(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    total_downloads = (
        db.query(func.count(ActivityLog.id))
        .filter(
            ActivityLog.action == "FILE_DOWNLOADED"
        )
        .scalar()
    )

    return {
        "download_activity": total_downloads
    }

@router.delete("/delete-user/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # Only ADMIN can delete users
    if current_user.role != "ADMIN":

        log_activity(
            db=db,
            user_id=current_user.id,
            action="UNAUTHORIZED_ACCESS",
            resource_type="USER",
            resource_id=user_id,
            description=(
                f"{current_user.username} attempted "
                f"to delete user {user_id} without admin permission"
            ),
            status="FAILED"
        )

        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    # Admin cannot delete their own account
    if current_user.id == user_id:

        raise HTTPException(
            status_code=400,
            detail="You cannot delete your own account."
        )

    # Find user
    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if user is None:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    username = user.username

    try:

        # -----------------------------------------
        # DELETE SHARES
        # -----------------------------------------

        db.query(Share).filter(
            Share.shared_with == user_id
        ).delete(
            synchronize_session=False
        )

        # If your Share model has a sender/owner column
        # such as shared_by, you can also delete those
        # records here if required.


        # -----------------------------------------
        # DELETE FILES
        # -----------------------------------------

        files = db.query(File).filter(
            File.owner_id == user_id
        ).all()

        for file in files:

            # Delete physical file if stored locally
            if getattr(file, "stored_filename", None):

                file_path = os.path.join(
                    "uploads",
                    file.stored_filename
                )

                if os.path.exists(file_path):

                    try:
                        os.remove(file_path)

                    except OSError:
                        pass

            db.delete(file)


        # -----------------------------------------
        # DELETE FOLDERS
        # -----------------------------------------

        folders = db.query(Folder).filter(
            Folder.owner_id == user_id
        ).all()

        for folder in folders:

            db.delete(folder)


        # -----------------------------------------
        # DELETE ACTIVITY LOGS
        # -----------------------------------------

        db.query(ActivityLog).filter(
            ActivityLog.user_id == user_id
        ).delete(
            synchronize_session=False
        )


        # -----------------------------------------
        # DELETE USER
        # -----------------------------------------

        db.delete(user)

        db.commit()


        # -----------------------------------------
        # LOG ADMIN ACTION
        # -----------------------------------------

        log_activity(
            db=db,
            user_id=current_user.id,
            action="USER_DELETED",
            resource_type="USER",
            resource_id=user_id,
            description=(
                f"{current_user.username} deleted "
                f"user {username}"
            ),
            status="SUCCESS"
        )

        return {
            "message": "User deleted successfully",
            "user_id": user_id,
            "username": username
        }


    except Exception as error:

        db.rollback()

        print("DELETE USER ERROR:", error)

        raise HTTPException(
            status_code=500,
            detail="Unable to delete user."
        )