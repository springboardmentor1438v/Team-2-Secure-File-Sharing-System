from pydantic import BaseModel, EmailStr


class VerifyEmailRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    password: str