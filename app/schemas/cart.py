from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field


class CartItemIn(BaseModel):
    gameId: int
    quantity: int = Field(1, ge=1)


class CartIn(BaseModel):
    userId: Optional[int] = None  # si no se manda, se usa el usuario del token
    date: Optional[date] = None
    products: List[CartItemIn]


class CartOut(BaseModel):
    id: int
    userId: int
    date: date
    products: List[CartItemIn]
