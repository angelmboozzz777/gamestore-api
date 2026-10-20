# GameStore API

API REST de videojuegos (estilo [FakeStoreAPI](https://fakestoreapi.com/)) hecha con **FastAPI + MongoDB (Atlas)**.
Responde JSON y esta lista para consumirse desde Flutter.

## 1. Instalacion

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Base de datos (MongoDB Atlas)

Los datos viven en MongoDB Atlas, base `gamestore`, con estas colecciones:

| Coleccion | Que guarda |
|---|---|
| `games` | videojuegos (`rating` va como subdocumento) |
| `users` | usuarios; `name` y `address` como subdocumentos; contrasena con hash bcrypt |
| `carts` | carritos; los productos van dentro del carrito: `products: [{gameId, quantity}]` |
| `counters` | ultimo id usado en cada coleccion (los ids son numeros 1, 2, 3..., como en MySQL) |

Copia `.env.example` a `.env` y pon tu cadena de conexion de Atlas
(Atlas -> Connect -> Drivers). **El `.env` no se sube a git** porque lleva tu contrasena.

```
MONGODB_URI=mongodb+srv://usuario:password@cluster0.xxxxx.mongodb.net/
MONGODB_DB=gamestore
SECRET_KEY=una-cadena-larga-y-aleatoria
```

Las colecciones se crean solas; al arrancar la API solo crea los indices
(`username` y `email` unicos). Nunca borra ni sobreescribe datos.

## 3. Arranque

```bash
python -m app
```

Al arrancar, la consola muestra las direcciones que si funcionan:

```
  GameStore API lista. Abrela en:
    Esta PC:          http://localhost:8000
    Emulador Android: http://10.0.2.2:8000
    Celular (WiFi):   http://192.168.x.x:8000
    Documentacion:    http://localhost:8000/docs
```

- `python -m app` equivale a `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
  (que tambien sigue funcionando). Otro puerto: `python -m app 8001`.
- `--host 0.0.0.0` hace que la API escuche en todas las redes (asi el emulador y el celular
  pueden conectarse), pero **http://0.0.0.0:8000 no se abre en el navegador** (`ERR_ADDRESS_INVALID`).
  En tu PC usa siempre http://localhost:8000.
- `GET /` devuelve el estado de la API, totales (juegos, usuarios, carritos) y la lista de endpoints.
- Documentacion interactiva: http://localhost:8000/docs
- Cada usuario tiene un rol en la columna `role` de la tabla `users`:

  | role | En la app | Puede |
  |---|---|---|
  | `admin` | Administrador | agregar, editar y eliminar juegos; comprar |
  | `auditor` | Auditor | solo consultar el catalogo (sin carrito) |
  | `user` | Cliente | comprar (es el rol por defecto al registrarse) |

  Para cambiarlo, en Atlas (Browse Collections -> `users`) edita el campo `role` del usuario,
  o desde `mongosh`: `db.users.updateOne({username: 'tu_usuario'}, {$set: {role: 'admin'}})`

## 4. Endpoints

| Metodo | Ruta | Acceso | Descripcion |
|---|---|---|---|
| GET | `/games` | publico | Lista juegos. Params: `limit`, `skip`, `sort=asc\|desc`, `category`, `q` |
| GET | `/games/{id}` | publico | Un juego |
| GET | `/games/categories` | publico | Lista de categorias |
| GET | `/games/category/{categoria}` | publico | Juegos de una categoria |
| POST | `/games` | admin | Crear juego |
| PUT | `/games/{id}` | admin | Actualizar (parcial) |
| DELETE | `/games/{id}` | admin | Eliminar |
| POST | `/users` | publico | Registrar usuario |
| GET | `/users/me` | token | Mi perfil |
| GET | `/users`, `/users/{id}` | admin / dueno | Consultar usuarios |
| PUT, DELETE | `/users/{id}` | dueno o admin | Editar / borrar |
| POST | `/auth/login` | publico | Devuelve `token` (JWT) |
| GET | `/carts` | token | Mis carritos (admin ve todos). Params: `limit`, `sort`, `startdate`, `enddate` |
| GET | `/carts/user/{user_id}` | dueno o admin | Carritos de un usuario |
| GET, PUT, DELETE | `/carts/{id}` | dueno o admin | Un carrito |
| POST | `/carts` | token | Crear carrito |
| DELETE | `/carts/{id}/products/{game_id}` | dueno o admin | Quitar un juego del carrito |

Los endpoints protegidos llevan el header `Authorization: Bearer <token>`.

### Ejemplos de JSON

`GET /games/6`

```json
{
  "id": 6,
  "title": "Hollow Knight",
  "price": 249.0,
  "description": "Metroidvania de aventura en un reino subterraneo de insectos.",
  "category": "Indie",
  "image": "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/367520/.../header.jpg",
  "platform": "PC",
  "stock": 90,
  "rating": { "rate": 4.9, "count": 4100 }
}
```

`POST /auth/login` con `{"username": "demo", "password": "demo123"}`

```json
{ "token": "eyJhbGciOi...", "token_type": "bearer",
  "user": { "id": 2, "email": "demo@gamestore.com", "username": "demo",
            "name": {"firstname": "Demo", "lastname": "Gamer"},
            "address": {"city": "Queretaro", "street": "Av. Universidad", "number": "100", "zipcode": "76000"},
            "phone": "4421234567", "role": "user", "is_admin": false } }
```

`POST /carts` (el `userId` se toma del token si no lo mandas)

```json
{ "date": "2026-10-13", "products": [ {"gameId": 1, "quantity": 2}, {"gameId": 5, "quantity": 1} ] }
```

## 5. Flutter

Mira `flutter_example/` (modelo `Game` y `ApiService`). Direccion base segun donde corras la app:

| Entorno | URL |
|---|---|
| Emulador Android | `http://10.0.2.2:8000` |
| iOS simulator | `http://localhost:8000` |
| Celular fisico (misma WiFi) | `http://IP_DE_TU_PC:8000` |

## 6. Publicar (GitHub + Vercel, como en tu clase)

1. Sube el proyecto a GitHub (el `.env` ya esta en `.gitignore`).
2. La base ya esta en la nube (MongoDB Atlas). Donde hospedes la API pon `MONGODB_URI`, `MONGODB_DB` y `SECRET_KEY` como variables de entorno, y en Atlas -> Network Access permite la IP de ese servidor.
3. Para Vercel agrega un `vercel.json` que apunte a `app/main.py` como funcion Python (o usa Railway/Render, que corren `uvicorn` directo y son mas sencillos para FastAPI).

## Estructura

```
app/
  __main__.py    # arranque con: python -m app
  main.py        # app FastAPI, CORS, routers
  database.py    # conexion a MongoDB e ids numericos
  models.py      # forma de los documentos y su JSON
  schemas.py     # validacion / JSON de entrada y salida
  security.py    # bcrypt + JWT
  routers/       # games, users, carts, auth
flutter_example/ # modelo y servicio para tu app
```
