from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


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
