"""Forma de los documentos en MongoDB y conversion a JSON de la API.

Colecciones (base "gamestore"):

games  { _id: 1, title, price, description, category, image, platform, stock,
         rating: { rate, count } }
users  { _id: 1, email, username, password (hash bcrypt),
         name: { firstname, lastname },
         address: { city, street, number, zipcode },
         phone, role }
carts  { _id: 1, userId, date: "2026-10-20",
         products: [ { gameId, quantity } ] }
counters { _id: "games", valor: 14 }   <- ultimo id usado en cada coleccion
"""

# Roles posibles en users.role
ROL_ADMIN = "admin"
ROL_AUDITOR = "auditor"
ROL_USUARIO = "user"


def es_admin(usuario: dict) -> bool:
    return usuario.get("role") == ROL_ADMIN


def game_out(doc: dict) -> dict:
    rating = doc.get("rating") or {}
    return {
        "id": doc["_id"],
        "title": doc["title"],
        "price": float(doc["price"]),
        "description": doc.get("description", ""),
        "category": doc["category"],
        "image": doc.get("image", ""),
        "platform": doc.get("platform", "PC"),
        "stock": doc.get("stock", 0),
        "rating": {"rate": rating.get("rate", 0), "count": rating.get("count", 0)},
    }


def user_out(doc: dict) -> dict:
    name = doc.get("name") or {}
    address = doc.get("address") or {}
    return {
        "id": doc["_id"],
        "email": doc["email"],
        "username": doc["username"],
        "name": {
            "firstname": name.get("firstname", ""),
            "lastname": name.get("lastname", ""),
        },
        "address": {
            "city": address.get("city", ""),
            "street": address.get("street", ""),
            "number": address.get("number", ""),
            "zipcode": address.get("zipcode", ""),
        },
        "phone": doc.get("phone", ""),
        "role": doc.get("role", ROL_USUARIO),
        "is_admin": es_admin(doc),
    }


def cart_out(doc: dict) -> dict:
    return {
        "id": doc["_id"],
        "userId": doc["userId"],
        "date": doc["date"],
        "products": [
            {"gameId": p["gameId"], "quantity": p["quantity"]}
            for p in doc.get("products", [])
        ],
    }
