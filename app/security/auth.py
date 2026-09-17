from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.security.jwt_handler import verify_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):

    payload = verify_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or Expired Token"
        )

    email = payload.get("sub")

    user = db.query(User).filter(
        User.email == email
    ).first()

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User Not Found"
        )

    return user