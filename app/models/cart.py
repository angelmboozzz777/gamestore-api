"""Coleccion carts: documento de Mongo -> JSON de la API."""


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
