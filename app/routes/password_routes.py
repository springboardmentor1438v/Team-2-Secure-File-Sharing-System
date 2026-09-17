from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.schemas.password_schema import (
    VerifyEmailRequest,
    ResetPasswordRequest,
)

from app.security.hash import hash_password

router = APIRouter(tags=["Password"])


@router.post("/verify-email")
def verify_email(
    request: VerifyEmailRequest,
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(
        User.email == request.email
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="Email not found"
        )

    return {
        "message": "Email verified"
    }


@router.put("/reset-password")
def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(
        User.email == request.email
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="Email not found"
        )

    user.password = hash_password(request.password)

    db.commit()

    return {
        "message": "Password updated successfully"
    }