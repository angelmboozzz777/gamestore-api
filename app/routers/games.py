import re
from typing import List, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pymongo import ASCENDING, DESCENDING
from pymongo.database import Database

from ..core.database import get_db, siguiente_id
from ..core.security import require_admin
from ..models.game import game_out
from ..schemas.game import GameCreate, GameOut, GameUpdate

router = APIRouter(prefix="/games", tags=["Games"])


def _list(db: Database, category: Optional[str], q: Optional[str],
          limit: Optional[int], skip: int, sort: str):
    filtro = {}
    if category:
        filtro["category"] = category
    if q:
        # Busca el texto dentro del titulo, sin importar mayusculas.
        filtro["title"] = {"$regex": re.escape(q), "$options": "i"}
    cursor = db.games.find(filtro).sort("_id", ASCENDING if sort == "asc" else DESCENDING)
    if skip:
        cursor = cursor.skip(skip)
    if limit:
        cursor = cursor.limit(limit)
    return [game_out(g) for g in cursor]


def _get_or_404(db: Database, game_id: int) -> dict:
    game = db.games.find_one({"_id": game_id})
    if game is None:
        raise HTTPException(status_code=404, detail="Videojuego no encontrado")
    return game


@router.get("", response_model=List[GameOut], summary="Listar videojuegos")
def list_games(
    limit: Optional[int] = Query(None, ge=1, le=100),
    skip: int = Query(0, ge=0),
    sort: Literal["asc", "desc"] = "asc",
    category: Optional[str] = None,
    q: Optional[str] = Query(None, description="Buscar por titulo"),
    db: Database = Depends(get_db),
):
    return _list(db, category, q, limit, skip, sort)


@router.get("/categories", response_model=List[str], summary="Listar categorias")
def list_categories(db: Database = Depends(get_db)):
    return sorted(db.games.distinct("category"))


@router.get("/category/{category}", response_model=List[GameOut], summary="Juegos por categoria")
def games_by_category(
    category: str,
    limit: Optional[int] = Query(None, ge=1, le=100),
    sort: Literal["asc", "desc"] = "asc",
    db: Database = Depends(get_db),
):
    return _list(db, category, None, limit, 0, sort)


@router.get("/{game_id}", response_model=GameOut, summary="Obtener un videojuego")
def get_game(game_id: int, db: Database = Depends(get_db)):
    return game_out(_get_or_404(db, game_id))


@router.post("", response_model=GameOut, status_code=201, summary="Crear videojuego (admin)")
def create_game(data: GameCreate, db: Database = Depends(get_db), _=Depends(require_admin)):
    game = {
        "_id": siguiente_id(db, "games"),
        **data.model_dump(),
        "rating": {"rate": 0, "count": 0},
    }
    db.games.insert_one(game)
    return game_out(game)


@router.put("/{game_id}", response_model=GameOut, summary="Actualizar videojuego (admin)")
def update_game(game_id: int, data: GameUpdate, db: Database = Depends(get_db),
                _=Depends(require_admin)):
    _get_or_404(db, game_id)
    cambios = data.model_dump(exclude_unset=True)
    if cambios:
        db.games.update_one({"_id": game_id}, {"$set": cambios})
    return game_out(_get_or_404(db, game_id))


@router.delete("/{game_id}", response_model=GameOut, summary="Eliminar videojuego (admin)")
def delete_game(game_id: int, db: Database = Depends(get_db), _=Depends(require_admin)):
    game = _get_or_404(db, game_id)
    # Tambien se quita de todos los carritos donde estaba.
    db.carts.update_many(
        {"products.gameId": game_id},
        {"$pull": {"products": {"gameId": game_id}}},
    )
    db.games.delete_one({"_id": game_id})
    return game_out(game)
