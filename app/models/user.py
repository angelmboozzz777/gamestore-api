"""Coleccion users: roles y documento de Mongo -> JSON de la API."""

# Roles posibles en users.role
ROL_ADMIN = "admin"
ROL_AUDITOR = "auditor"
ROL_USUARIO = "user"


def es_admin(usuario: dict) -> bool:
    return usuario.get("role") == ROL_ADMIN


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
