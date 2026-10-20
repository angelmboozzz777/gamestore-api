from fastapi import APIRouter, Depends, HTTPException
from pymongo.database import Database

from ..database import get_db
from ..models import user_out
from ..schemas import LoginIn, TokenOut
from ..security import create_token, verify_password

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=TokenOut)
def login(data: LoginIn, db: Database = Depends(get_db)):
    # Se puede entrar con el usuario o con el correo.
    user = db.users.find_one(
        {"$or": [{"username": data.username}, {"email": data.username}]}
    )
    if user is None or not verify_password(data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Usuario o contrasena incorrectos")
    return {"token": create_token(user["_id"]), "user": user_out(user)}
