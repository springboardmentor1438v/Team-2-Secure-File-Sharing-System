from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
class UserLogin(BaseModel):
    email: EmailStr
    password: str

from pydantic import BaseModel

class ChangeRoleRequest(BaseModel):
    role: str