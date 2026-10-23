import os
import socket
import sys
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pymongo.database import Database

from .core.database import MONGODB_DB, crear_indices, db as base_de_datos, get_db
from .routers import auth, carts, games, users


def puerto_actual() -> int:
    """Puerto con el que se arranco uvicorn (--port 8000 por defecto)."""
    args = sys.argv
    for i, arg in enumerate(args):
        if arg == "--port" and i + 1 < len(args):
            return int(args[i + 1])
        if arg.startswith("--port="):
            return int(arg.split("=", 1)[1])
    return 8000


def ip_local() -> str:
    """IP de esta PC en la red WiFi (para probar desde un celular fisico)."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))  # no envia nada, solo elige la interfaz
            return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Mongo crea las colecciones solas al insertar; aqui solo los indices.
    crear_indices(base_de_datos)
    # 0.0.0.0 solo significa "escuchar en todas las interfaces";
    # no es una direccion que se pueda abrir en el navegador.
    url_publica = os.getenv("RENDER_EXTERNAL_URL")
    if url_publica:  # corriendo en Render
        print(f"  GameStore API lista en {url_publica}  (docs: {url_publica}/docs)")
        yield
        return
    port = puerto_actual()
    print()
    print("  GameStore API lista. Abrela en:")
    print(f"    Esta PC:          http://localhost:{port}")
    print(f"    Emulador Android: http://10.0.2.2:{port}")
    print(f"    Celular (WiFi):   http://{ip_local()}:{port}")
    print(f"    Documentacion:    http://localhost:{port}/docs")
    print(f"  (No abras http://0.0.0.0:{port}: el navegador no la acepta)")
    print()
    yield


app = FastAPI(
    title="GameStore API",
    version="1.0.0",
    description="API REST de videojuegos (estilo FakeStoreAPI) con FastAPI + MongoDB.",
    lifespan=lifespan,
)

# Abierto para desarrollo; en produccion limita allow_origins a tus dominios.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(games.router)
app.include_router(users.router)
app.include_router(carts.router)
app.include_router(auth.router)


@app.get("/", tags=["Root"])
def root(request: Request, db: Database = Depends(get_db)):
    base = str(request.base_url).rstrip("/")
    return {
        "name": "GameStore API",
        "version": app.version,
        "description": app.description,
        "status": "ok",
        "base_url": base,
        "docs": f"{base}/docs",
        "database": MONGODB_DB,
        "totals": {
            "games": db.games.count_documents({}),
            "categories": len(db.games.distinct("category")),
            "users": db.users.count_documents({}),
            "carts": db.carts.count_documents({}),
        },
        "endpoints": {
            "games": {
                "GET /games": "Lista juegos (limit, skip, sort, category, q)",
                "GET /games/{id}": "Un juego",
                "GET /games/categories": "Categorias",
                "GET /games/category/{categoria}": "Juegos de una categoria",
                "POST /games": "Crear juego (admin)",
                "PUT /games/{id}": "Editar juego (admin)",
                "DELETE /games/{id}": "Eliminar juego (admin)",
            },
            "auth": {
                "POST /auth/login": "Devuelve token JWT y datos del usuario",
            },
            "users": {
                "POST /users": "Registrar usuario",
                "GET /users/me": "Mi perfil (token)",
                "GET /users": "Listar usuarios (admin)",
                "GET|PUT|DELETE /users/{id}": "Consultar / editar / borrar (dueno o admin)",
            },
            "carts": {
                "GET /carts": "Mis carritos (token)",
                "GET /carts/user/{user_id}": "Carritos de un usuario",
                "POST /carts": "Crear carrito",
                "GET|PUT|DELETE /carts/{id}": "Ver / reemplazar productos / borrar carrito",
                "DELETE /carts/{id}/products/{game_id}": "Quitar un juego del carrito",
            },
        },
        "auth_header": "Authorization: Bearer <token>",
    }


@app.get("/health", tags=["Root"])
def health():
    return {"status": "ok"}
