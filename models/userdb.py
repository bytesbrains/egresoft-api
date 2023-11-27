from pydantic import BaseModel
from typing import Optional
from passlib.hash import bcrypt
from enum import Enum


class UserRole(str, Enum):
    graduate = "graduate"
    admin = "admin"
    employer = "employer"


class User(BaseModel):
    id: str
    email: str
    disabled: bool
    password: str
    role: Optional[UserRole] = None


class UserDB(User):
    hashed_password: str


def hash_password(password: str) -> str:
    return bcrypt.hash(password)


# def verify_password(plain_password: str, hashed_password: str) -> bool:
#   return bcrypt.verify(plain_password, hashed_password)


class Config:
    allow_mutation = False
    extra = "allow"
