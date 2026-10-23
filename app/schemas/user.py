from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


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
