import os

from dotenv import load_dotenv
from pymongo import ASCENDING, MongoClient, ReturnDocument
from pymongo.database import Database

load_dotenv()

# Cadena de conexion de MongoDB Atlas (o un Mongo local), en el .env:
#   MONGODB_URI=mongodb+srv://usuario:password@cluster0.xxxxx.mongodb.net/
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DB = os.getenv("MONGODB_DB", "gamestore")

client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=10000)
db: Database = client[MONGODB_DB]


def get_db() -> Database:
    return db


def siguiente_id(base: Database, coleccion: str) -> int:
    """Id numerico autoincremental (1, 2, 3...), como el AUTO_INCREMENT de MySQL.

    La app de Flutter trabaja con ids enteros, asi que no usamos el ObjectId
    de Mongo. El ultimo id de cada coleccion se guarda en "counters".
    """
    contador = base.counters.find_one_and_update(
        {"_id": coleccion},
        {"$inc": {"valor": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )
    return contador["valor"]


def crear_indices(base: Database) -> None:
    """Indices equivalentes a los que tenian las tablas de MySQL."""
    base.users.create_index([("username", ASCENDING)], unique=True)
    base.users.create_index([("email", ASCENDING)], unique=True)
    base.games.create_index([("title", ASCENDING)])
    base.games.create_index([("category", ASCENDING)])
    base.carts.create_index([("userId", ASCENDING)])
