"""Coleccion games: documento de Mongo -> JSON de la API."""


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
