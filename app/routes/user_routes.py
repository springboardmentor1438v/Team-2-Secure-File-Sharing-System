from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from app.schemas.user_schema import UserCreate
from app.database.database import get_db
from app.models.user import User
from app.security.hash import hash_password, verify_password
from app.security.jwt_handler import create_access_token
from app.security.auth import get_current_user
from app.services.activity_service import log_activity


router = APIRouter()


@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):

    existing_user = db.query(User).filter(
        User.username == user.username
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    existing_email = db.query(User).filter(
        User.email == user.email
    ).first()

    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    hashed_password = hash_password(user.password)

    new_user = User(
        username=user.username,
        email=user.email,
        password=hashed_password,
        role="USER"
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    log_activity(
        db=db,
        user_id=new_user.id,
        action="USER_REGISTERED",
        resource_type="USER",
        resource_id=new_user.id,
        description=f"{new_user.username} registered successfully",
        status="SUCCESS"
    )

    return {
        "message": "Registration API Created Successfully"
    }


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    existing_user = db.query(User).filter(
        User.email == form_data.username
    ).first()

    if not existing_user:

        log_activity(
            db=db,
            user_id=None,
            action="LOGIN_FAILED",
            resource_type="USER",
            description=f"Login failed for email: {form_data.username}",
            status="FAILED"
        )

        raise HTTPException(
            status_code=401,
            detail="Invalid Email or Password"
        )

    if not verify_password(
        form_data.password,
        existing_user.password
    ):

        log_activity(
            db=db,
            user_id=existing_user.id,
            action="LOGIN_FAILED",
            resource_type="USER",
            resource_id=existing_user.id,
            description=f"Wrong password for {existing_user.username}",
            status="FAILED"
        )

        raise HTTPException(
            status_code=401,
            detail="Invalid Email or Password"
        )

    access_token = create_access_token(
        data={
            "sub": existing_user.email,
            "role": existing_user.role
        }
    )

    log_activity(
        db=db,
        user_id=existing_user.id,
        action="LOGIN_SUCCESS",
        resource_type="USER",
        resource_id=existing_user.id,
        description=f"{existing_user.username} logged in successfully",
        status="SUCCESS"
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get("/profile")
def profile(current_user: User = Depends(get_current_user)):

    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role
    }