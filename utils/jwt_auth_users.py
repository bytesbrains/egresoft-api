from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from schemas.user import user_schema
from database.client import db_client
from models.user import User, UserDB
import os

from dotenv import load_dotenv

load_dotenv()


ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_DURATION = int(os.getenv("ACCESS_TOKEN_DURATION"))
SECRET = os.getenv("SECRET")


crypt = CryptContext(schemes=["bcrypt"])

oauth2 = OAuth2PasswordBearer(tokenUrl="login")

exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Credenciales de Autenticación Invalidas",
    headers={"WWW.Authenticate": "Bearer"},
)


def search_user_db(username: str):
    try:
        user = db_client.users.find_one({"username": username})
        if user:
            return UserDB(**user_schema(user))
        else:
            return None  # Si no se encuentra el usuario, devolver None
    except Exception as e:
        print(f"Error al buscar usuario en la base de datos: {e}")
        return None



def search_user(username: str):
    try:
        user = db_client.users.find_one({"username": username})
        if user:
            return User(**user_schema(user))
        else:
            return None  # Si no se encuentra el usuario, devolver None
    except Exception as e:
        print(f"Error al buscar usuario en la base de datos: {e}")
        return None



# Autenticacion de usuario encriptado
async def auth_user(token: str = Depends(oauth2)):

    exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales de autenticación inválidas",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        # Decodifica el token para obtener el nombre de usuario
        username = jwt.decode(token, SECRET, algorithms=[ALGORITHM]).get("sub")
        if username is None:
            raise exception

    except JWTError:
        raise exception

    # Utiliza la función search_user para buscar el usuario en la base de datos
    user = search_user(username)

    if user is None:
        raise exception

    return user


# si el usuario está inactivo (disabled), enviar mensaje
async def current_user(user: User = Depends(auth_user)):
    # Utiliza la función search_user para obtener el usuario actualizado de la base de datos
    user = search_user(user.username)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario no encontrado"
        )

    if user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario inactivo"
        )

    return user
