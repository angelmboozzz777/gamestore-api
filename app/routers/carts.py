from datetime import date as Date
from typing import List, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pymongo import ASCENDING, DESCENDING
from pymongo.database import Database

from ..database import get_db, siguiente_id
from ..models import cart_out, es_admin
from ..schemas import CartIn, CartOut
from ..security import get_current_user

router = APIRouter(prefix="/carts", tags=["Carts"])


def _build_items(db: Database, products) -> List[dict]:
    """Junta los juegos repetidos y valida que todos existan."""
    merged = {}
    for p in products:
        merged[p.gameId] = merged.get(p.gameId, 0) + p.quantity
    if merged:
        found = {g["_id"] for g in db.games.find({"_id": {"$in": list(merged)}}, {"_id": 1})}
        missing = set(merged) - found
        if missing:
            raise HTTPException(status_code=404, detail=f"Videojuegos no encontrados: {sorted(missing)}")
    return [{"gameId": g, "quantity": q} for g, q in merged.items()]


def _get_cart_or_404(db: Database, cart_id: int, current: dict) -> dict:
    cart = db.carts.find_one({"_id": cart_id})
    if cart is None:
        raise HTTPException(status_code=404, detail="Carrito no encontrado")
    if cart["userId"] != current["_id"] and not es_admin(current):
        raise HTTPException(status_code=403, detail="No tienes permiso para este carrito")
    return cart


@router.get("", response_model=List[CartOut], summary="Listar carritos (propios; admin ve todos)")
def list_carts(
    limit: Optional[int] = Query(None, ge=1, le=100),
    sort: Literal["asc", "desc"] = "asc",
    startdate: Optional[Date] = None,
    enddate: Optional[Date] = None,
    db: Database = Depends(get_db),
    current: dict = Depends(get_current_user),
):
    filtro = {}
    if not es_admin(current):
        filtro["userId"] = current["_id"]
    # Las fechas se guardan como texto "AAAA-MM-DD", que se ordena igual que la fecha.
    rango = {}
    if startdate:
        rango["$gte"] = startdate.isoformat()
    if enddate:
        rango["$lte"] = enddate.isoformat()
    if rango:
        filtro["date"] = rango
    cursor = db.carts.find(filtro).sort("_id", ASCENDING if sort == "asc" else DESCENDING)
    if limit:
        cursor = cursor.limit(limit)
    return [cart_out(c) for c in cursor]


@router.get("/user/{user_id}", response_model=List[CartOut], summary="Carritos de un usuario")
def carts_by_user(user_id: int, db: Database = Depends(get_db),
                  current: dict = Depends(get_current_user)):
    if user_id != current["_id"] and not es_admin(current):
        raise HTTPException(status_code=403, detail="No tienes permiso para esta accion")
    return [cart_out(c) for c in db.carts.find({"userId": user_id}).sort("_id", ASCENDING)]


@router.get("/{cart_id}", response_model=CartOut, summary="Obtener un carrito")
def get_cart(cart_id: int, db: Database = Depends(get_db),
             current: dict = Depends(get_current_user)):
    return cart_out(_get_cart_or_404(db, cart_id, current))


@router.post("", response_model=CartOut, status_code=201, summary="Crear carrito")
def create_cart(data: CartIn, db: Database = Depends(get_db),
                current: dict = Depends(get_current_user)):
    user_id = data.userId or current["_id"]
    if user_id != current["_id"] and not es_admin(current):
        raise HTTPException(status_code=403, detail="No puedes crear carritos para otro usuario")
    if db.users.find_one({"_id": user_id}, {"_id": 1}) is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    cart = {
        "_id": siguiente_id(db, "carts"),
        "userId": user_id,
        "date": (data.date or Date.today()).isoformat(),
        "products": _build_items(db, data.products),
    }
    db.carts.insert_one(cart)
    return cart_out(cart)


@router.put("/{cart_id}", response_model=CartOut, summary="Reemplazar productos de un carrito")
def update_cart(cart_id: int, data: CartIn, db: Database = Depends(get_db),
                current: dict = Depends(get_current_user)):
    _get_cart_or_404(db, cart_id, current)
    cambios = {"products": _build_items(db, data.products)}
    if data.date:
        cambios["date"] = data.date.isoformat()
    db.carts.update_one({"_id": cart_id}, {"$set": cambios})
    return cart_out(_get_cart_or_404(db, cart_id, current))


@router.delete("/{cart_id}", response_model=CartOut, summary="Eliminar carrito")
def delete_cart(cart_id: int, db: Database = Depends(get_db),
                current: dict = Depends(get_current_user)):
    cart = _get_cart_or_404(db, cart_id, current)
    db.carts.delete_one({"_id": cart_id})
    return cart_out(cart)


@router.delete("/{cart_id}/products/{game_id}", response_model=CartOut,
               summary="Quitar un videojuego del carrito")
def remove_cart_product(cart_id: int, game_id: int, db: Database = Depends(get_db),
                        current: dict = Depends(get_current_user)):
    cart = _get_cart_or_404(db, cart_id, current)
    if not any(p["gameId"] == game_id for p in cart.get("products", [])):
        raise HTTPException(status_code=404, detail="Ese videojuego no esta en el carrito")
    db.carts.update_one({"_id": cart_id}, {"$pull": {"products": {"gameId": game_id}}})
    return cart_out(_get_cart_or_404(db, cart_id, current))
