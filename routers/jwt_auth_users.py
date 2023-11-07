from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta
from fastapi import APIRouter
import json
import os

router = APIRouter(
    prefix="/users", tags=["users"], responses={404: {"message": "No encontrado"}}
)


# Correr la API con:   uvicorn jwt_auth_users:app --reload

ALGORITHM = "HS256"
ACCESS_TOKEN_DURATION = 1
SECRET = "5fa869be0c3678d8e333fab950e66a79afd81517ad7dba3b596353fca0e6ee71"

crypt = CryptContext(schemes=["bcrypt"])


oauth2 = OAuth2PasswordBearer(tokenUrl="login")


class User(BaseModel):  # modelo db
    username: str
    full_name: str
    email: str
    disabled: bool


class UserDB(User):
    password: str


# Specify the absolute path to db.json
json_file_path = os.path.join(os.path.dirname(__file__), "../db.json")


# Open and read the JSON file
with open(json_file_path, "r") as json_file:
    users_db = json.load(json_file)

exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Credenciales de Autenticación Invalidas",
    headers={"WWW.Authenticate": "Bearer"},
)


def search_user_db(username: str):
    if username in users_db:
        return UserDB(**users_db[username])


def search_user(username: str):
    if username in users_db:
        return User(**users_db[username])  # retornar users del arreglo


# Autenticacion de usuario encriptado
async def auth_user(token: str = Depends(oauth2)):
    try:
        username = jwt.decode(token, SECRET, algorithms=[ALGORITHM]).get("sub")
        if username is None:
            raise exception

    except JWTError:
        raise exception

    return search_user(username)


# si el user esta inactivo= disabled mandar mensaje
async def current_user(user: User = Depends(auth_user)):
    if user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario inactivo"
        )

    return user


# form username and password
@router.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    user_db = users_db.get(form.username)
    if not user_db:
        raise HTTPException(status_code=400, detail="Error el usuario no es correcto")

    user = search_user_db(form.username)

    if not crypt.verify(form.password, user.password):
        raise HTTPException(
            status_code=400, detail="Error la contraseña no es correcta"
        )

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_DURATION)

    access_token = {
        "sub": user.username,
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_DURATION),
    }

    return {
        "access_token": jwt.encode(access_token, SECRET, algorithm=ALGORITHM),
        "token_type": "bearer",
    }


@router.get("/me")  # verificar token de user usando current_user
async def me(user: User = Depends(current_user)):
    return user
