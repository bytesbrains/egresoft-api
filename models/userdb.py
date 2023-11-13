from pydantic import BaseModel,Field
from typing import Optional
from bson import ObjectId
from passlib.hash import bcrypt

class User(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    username: str
    full_name: str
    email: str
    disabled: bool
    password: str

class UserDB(User):
    hashed_password: str

def hash_password(password: str) -> str:
    return bcrypt.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.verify(plain_password, hashed_password)

class Config:
        allow_mutation = False
        extra = "allow"
