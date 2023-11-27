from pydantic import BaseModel
from typing import Optional
from enum import Enum


class UserRole(str, Enum):
    graduate = "graduate"
    admin = "admin"
    employer = "employer"


class User(BaseModel):
    id: str
    email: str
    disabled: bool
    role: Optional[UserRole] = None


class UserDB(User):
    password: str


class Config:
    allow_mutation = False
    extra = "allow"
