from datetime import date
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


# ---------- Games ----------
class Rating(BaseModel):
    rate: float = 0
    count: int = 0


class GameBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    price: float = Field(gt=0)
    description: str = ""
    category: str = Field(min_length=1, max_length=80)
    image: str = ""
    platform: str = "PC"
    stock: int = Field(0, ge=0)


class GameCreate(GameBase):
    pass


class GameUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    price: Optional[float] = Field(None, gt=0)
    description: Optional[str] = None
    category: Optional[str] = None
    image: Optional[str] = None
    platform: Optional[str] = None
    stock: Optional[int] = Field(None, ge=0)


class GameOut(GameBase):
    id: int
    rating: Rating

    model_config = ConfigDict(from_attributes=True)


# ---------- Users ----------
class Name(BaseModel):
    firstname: str = ""
    lastname: str = ""


class Address(BaseModel):
    city: str = ""
    street: str = ""
    number: str = ""
    zipcode: str = ""


class UserCreate(BaseModel):
    email: str = Field(min_length=5, max_length=120)
    username: str = Field(min_length=3, max_length=60)
    password: str = Field(min_length=6, max_length=72)
    name: Name = Field(default_factory=Name)
    address: Address = Field(default_factory=Address)
    phone: str = ""


class UserUpdate(BaseModel):
    email: Optional[str] = Field(None, min_length=5, max_length=120)
    username: Optional[str] = Field(None, min_length=3, max_length=60)
    password: Optional[str] = Field(None, min_length=6, max_length=72)
    name: Optional[Name] = None
    address: Optional[Address] = None
    phone: Optional[str] = None


class UserOut(BaseModel):
    id: int
    email: str
    username: str
    name: Name
    address: Address
    phone: str
    role: str  # admin | auditor | user
    is_admin: bool

    model_config = ConfigDict(from_attributes=True)


# ---------- Auth ----------
class LoginIn(BaseModel):
    username: str  # tambien acepta el email
    password: str


class TokenOut(BaseModel):
    token: str
    token_type: str = "bearer"
    user: UserOut


# ---------- Carts ----------
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
