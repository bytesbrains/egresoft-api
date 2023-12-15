import os
from dotenv import load_dotenv

from fastapi import HTTPException, APIRouter, status, Form, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy import cast, String
from sqlalchemy import func
from sqlalchemy import or_
from database.client import db_client
from database.database import get_db, engine
from models.models import EgresadoBasico, Base
from utils.changePassword import (
    send_password_reset_email,
    verify_token,
    update_password,
    generate_reset_token,
)


load_dotenv()
Base.metadata.create_all(bind=engine)
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


@router.post("/password/reset-password")
async def forgot_password(email: str = Form(...), db: Session = Depends(get_db)):
    # Verificar si el correo existe en MongoDB
    user_mongo = db_client.graduates.find_one({"email": email})
    if user_mongo:
        # Generar y guardar un token de restablecimiento en MongoDB
        token = generate_reset_token(email)
        db_client.password_reset_tokens.insert_one({"email": email, "token": token})

        # Enviar correo electrónico con el token y el enlace de restablecimiento desde MongoDB
        reset_link = (
            f"https://www.egresoft.tech/login/password/reset-password?token={token}"
        )
        send_password_reset_email(email, reset_link)

        return {"message": "Correo electrónico enviado con éxito desde MongoDB"}

    # Si no se encuentra en MongoDB, buscar en PostgreSQL
    result = (
        db.query(EgresadoBasico)
        .filter(
            func.json_extract_path_text(EgresadoBasico.correo, "correo_personal")
            == email
        )
        .first()
    )

    if result:
        user_id = result.id_egre
        # Generar y guardar un token de restablecimiento en PostgreSQL
        token = generate_reset_token(email)
        db_client.password_reset_tokens.insert_one(
            {"id": user_id, "email": email, "token": token}
        )
        # Aquí se insertaría en la tabla correspondiente en PostgreSQL

        # Enviar correo electrónico con el token y el enlace de restablecimiento desde PostgreSQL
        reset_link = (
            f"https://www.egresoft.tech/login/password/reset-password?token={token}"
        )
        send_password_reset_email(email, reset_link)

        return {"message": "Correo electrónico enviado con éxito desde PostgreSQL"}

    raise HTTPException(status_code=404, detail="Correo electrónico no encontrado")


@router.post("/password/reset-password/{token}")
async def Set_reset_password(token: str, new_password: str = Form(...)):
    # Verificar la validez del token
    email = verify_token(token)

    # Actualizar la contraseña en la base de datos
    update_password(email, new_password)

    return {"message": "Contraseña restablecida con éxito"}
