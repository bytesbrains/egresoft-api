from fastapi import Depends, HTTPException, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm.exc import NoResultFound
from datetime import datetime, timedelta
from utils.jwt_auth_users import (
    search_user_db_graduate,
    crypt,
    current_user_graduate,
    search_user_db_admin,
    current_user_admin,
)
from jose import jwt
from models.user import User
from models.models import EgresadoBasico, AdministrativoBasico, Base
from schemas.user import postgres_user_schema, postgres_administrativo_schema
from database.database import engine, get_db
from sqlalchemy.orm import Session

Base.metadata.create_all(bind=engine)


import os


ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_DURATION = int(os.getenv("ACCESS_TOKEN_DURATION"))
SECRET = os.getenv("SECRET")

router = APIRouter(
    prefix="/users", tags=["users"], responses={404: {"message": "No encontrado"}}
)


### Apartir de aqui todo el login del Admin ###
@router.post("/login/graduate")
async def login(
    form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    try:
        user = search_user_db_graduate(form.username)

        if user is None:
            raise HTTPException(
                status_code=400, detail="Error: el usuario no es correcto"
            )

        # Verifica la contraseña utilizando el método verify de CryptContext
        if not crypt.verify_and_update(form.password, user.password)[0]:
            raise HTTPException(
                status_code=400, detail="Error: la contraseña no es correcta"
            )

        if user.disabled:
            raise HTTPException(
                status_code=400, detail="Error: el usuario está inactivo"
            )

        # Configuración del token de acceso
        access_token = {
            "sub": user.id,
            "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_DURATION),
        }

        # Devuelve el token de acceso
        return {
            "access_token": jwt.encode(access_token, SECRET, algorithm=ALGORITHM),
            "token_type": "bearer",
        }

    except HTTPException as e:
        return e
    except Exception as e:
        print(f"Error en la autenticación: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor en la autenticación: {str(e)}",
        )


# expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_DURATION)


@router.get("/me/graduate")  # verificar token de user usando current_user
async def me(
    user: User = Depends(current_user_graduate), db: Session = Depends(get_db)
):
    try:
        postgres_user = (
            db.query(EgresadoBasico).filter(EgresadoBasico.id_egre == user.id).one()
        )
        user_postgres = postgres_user_schema(postgres_user)
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Egresado no encontrado")

    # Fusionar los datos de usuario de ambas fuentes en un nuevo diccionario
    merged_user = {}
    if user:
        merged_user.update(user)
    if user_postgres:
        merged_user.update(user_postgres)

    return merged_user


### Apartir de aqui todo el login del Admin ###
@router.post("/login/admin")
async def login_admin(form: OAuth2PasswordRequestForm = Depends()):
    try:
        user = search_user_db_admin(form.username)

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
            "sub": user.id,
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


@router.get("/me/admin")  # verificar token de user usando current_user
async def me_admin(
    user: User = Depends(current_user_admin), db: Session = Depends(get_db)
):
    try:
        postgres_user = (
            db.query(AdministrativoBasico)
            .filter(AdministrativoBasico.id_adm == user.id)
            .one()
        )
        user_postgres = postgres_administrativo_schema(postgres_user)
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Administrativo no encontrado")

    # Fusionar los datos de usuario de ambas fuentes en un nuevo diccionario
    merged_user = {}
    if user:
        merged_user.update(user)
    if user_postgres:
        merged_user.update(user_postgres)

    return merged_user
