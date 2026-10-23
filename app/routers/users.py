from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pymongo import ASCENDING
from pymongo.database import Database
from pymongo.errors import DuplicateKeyError

from ..database import get_db, siguiente_id
from ..models import ROL_USUARIO, es_admin, user_out
from ..schemas import UserCreate, UserOut, UserUpdate
from ..security import get_current_user, hash_password, require_admin

router = APIRouter(prefix="/users", tags=["Users"])

YA_EXISTE = HTTPException(status_code=409, detail="El email o usuario ya existe")


def _check_free(db: Database, email, username, exclude_id=None):
    conds = []
    if email:
        conds.append({"email": email})
    if username:
        conds.append({"username": username})
    if not conds:
        return
    for u in db.users.find({"$or": conds}, {"_id": 1}):
        if u["_id"] != exclude_id:
            raise YA_EXISTE


def _own_or_admin(user_id: int, current: dict):
    if current["_id"] != user_id and not es_admin(current):
        raise HTTPException(status_code=403, detail="No tienes permiso para esta accion")


def _get_or_404(db: Database, user_id: int) -> dict:
    user = db.users.find_one({"_id": user_id})
    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


@router.post("", response_model=UserOut, status_code=201, summary="Registrar usuario")
def register(data: UserCreate, db: Database = Depends(get_db)):
    _check_free(db, data.email, data.username)
    user = {
        "_id": siguiente_id(db, "users"),
        **data.model_dump(),
        # El rol nunca lo elige quien se registra.
        "role": ROL_USUARIO,
    }
    user["password"] = hash_password(user["password"])
    try:
        db.users.insert_one(user)
    except DuplicateKeyError:
        raise YA_EXISTE
    return user_out(user)


@router.get("", response_model=List[UserOut], summary="Listar usuarios (admin)")
def list_users(db: Database = Depends(get_db), _=Depends(require_admin)):
    return [user_out(u) for u in db.users.find().sort("_id", ASCENDING)]


@router.get("/me", response_model=UserOut, summary="Mi perfil")
def me(current: dict = Depends(get_current_user)):
    return user_out(current)


@router.get("/{user_id}", response_model=UserOut, summary="Obtener usuario")
def get_user(user_id: int, db: Database = Depends(get_db),
             current: dict = Depends(get_current_user)):
    _own_or_admin(user_id, current)
    return user_out(_get_or_404(db, user_id))


@router.put("/{user_id}", response_model=UserOut, summary="Actualizar usuario")
def update_user(user_id: int, data: UserUpdate, db: Database = Depends(get_db),
                current: dict = Depends(get_current_user)):
    _own_or_admin(user_id, current)
    _get_or_404(db, user_id)
    valores = data.model_dump(exclude_unset=True)
    _check_free(db, valores.get("email"), valores.get("username"), exclude_id=user_id)

    # name y address son subdocumentos: solo se cambian los campos enviados.
    cambios = {}
    for clave, valor in valores.items():
        if clave in ("name", "address") and isinstance(valor, dict):
            for sub, v in valor.items():
                cambios[f"{clave}.{sub}"] = v
        elif clave == "password":
            cambios["password"] = hash_password(valor)
        else:
            cambios[clave] = valor

    if cambios:
        try:
            db.users.update_one({"_id": user_id}, {"$set": cambios})
        except DuplicateKeyError:
            raise YA_EXISTE
    return user_out(_get_or_404(db, user_id))


@router.delete("/{user_id}", response_model=UserOut, summary="Eliminar usuario")
def delete_user(user_id: int, db: Database = Depends(get_db),
                current: dict = Depends(get_current_user)):
    _own_or_admin(user_id, current)
    user = _get_or_404(db, user_id)
    # Sus carritos se borran con el.
    db.carts.delete_many({"userId": user_id})
    db.users.delete_one({"_id": user_id})
    return user_out(user)
