from fastapi import Depends, HTTPException, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from utils.jwt_auth_users import search_user_db, crypt, current_user
from jose import jwt
from models.user import User
import os

ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_DURATION = int(os.getenv("ACCESS_TOKEN_DURATION"))
SECRET = os.getenv("SECRET")

router = APIRouter(
    prefix="/users", tags=["users"], responses={404: {"message": "No encontrado"}}
)


@router.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    try:
        user = search_user_db(form.username)

        if not user:
            raise HTTPException(
                status_code=400, detail="Error: el usuario no es correcto"
            )

        if not crypt.verify(form.password, user.password):
            raise HTTPException(
                status_code=400, detail="Error: la contraseña no es correcta"
            )

        if user.disabled:
            raise HTTPException(
                status_code=400, detail="Error: el usuario está inactivo"
            )

        # Configuración del token de acceso
        access_token = {
            "sub": user.username,
            "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_DURATION),
        }

        # Devuelve el token de acceso
        return {
            "access_token": jwt.encode(access_token, SECRET, algorithm=ALGORITHM),
            "token_type": "bearer",
        }

    except Exception as e:
        print(f"Error en la autenticación: {e}")
        raise HTTPException(
            status_code=500, detail="Error interno del servidor en la autenticación"
        )

# expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_DURATION)


@router.get("/me")  # verificar token de user usando current_user
async def me(user: User = Depends(current_user)):
    return user
