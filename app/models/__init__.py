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

Un archivo por coleccion: game.py, user.py, cart.py.
"""
