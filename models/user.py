from pydantic import BaseModel
from typing import Optional
from enum import Enum
from datetime import datetime


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


class TokenPayload(BaseModel):
    email: str
    exp: datetime


class Config:
    allow_mutation = False
    extra = "allow"
