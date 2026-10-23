from pydantic import BaseModel

from .user import UserOut


class LoginIn(BaseModel):
    username: str  # tambien acepta el email
    password: str


class TokenOut(BaseModel):
    token: str
    token_type: str = "bearer"
    user: UserOut
