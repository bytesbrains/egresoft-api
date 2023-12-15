from fastapi import Depends, HTTPException, APIRouter, status, Form
from database.client import db_client
from fastapi.security import OAuth2PasswordBearer
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from utils.changePassword import (
    send_password_reset_email,
    verify_token,
    update_password,
    generate_reset_token,
)
import os

from dotenv import load_dotenv

load_dotenv()

templates = Jinja2Templates(directory="templates")
router = APIRouter(
    prefix="/login",
    tags=["Cambiar Contraseña Egresado"],
    responses={404: {"message": "No encontrado"}},
)

exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Credenciales de Autenticación Invalidas",
    headers={"WWW.Authenticate": "Bearer"},
)

db = db_client

# Configuración de OAuth2 para el manejo de tokens
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Rutas


@router.post("/password")
async def forgot_password(email: str = Form(...)):
    # Verificar si el correo existe en la base de datos
    user = db.graduates.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="Correo electrónico no encontrado")

    # Generar y guardar un token de restablecimiento en la base de datos
    token = generate_reset_token(email)
    db.password_reset_tokens.insert_one({"email": email, "token": token})

    # Enviar correo electrónico con el token y el enlace de restablecimiento
    reset_link = f"https://www.egresoft.tech/login/password?token={token}"
    send_password_reset_email(email, reset_link)

    return {"message": "Correo electrónico enviado con éxito"}


@router.post("/password/{token}")
async def Set_reset_password(token: str, new_password: str = Form(...)):
    # Verificar la validez del token
    email = verify_token(token)

    # Actualizar la contraseña en la base de datos
    update_password(email, new_password)

    return {"message": "Contraseña restablecida con éxito"}
