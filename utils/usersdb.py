from fastapi import Depends, HTTPException
from models.userdb import User, UserPM
from schemas.user import user_schema, postgres_user_schema, user_schemaPM
from sqlalchemy.orm.exc import NoResultFound
from database.client import db_client
from models.models import EgresadoBasico, Base
from database.database import engine, get_db
from sqlalchemy.orm import Session

Base.metadata.create_all(bind=engine)


# si se usa un metodo, deben de estar abajo del todo que se uso
# get de usuarios con try catch
def search_user(field: str, key):
    try:
        user = db_client.graduates.find_one({field: key})
        if user:
            return User(**user_schema(user))
        else:
            return None  # Si no se encuentra el usuario, devolver None
    except Exception as e:
        print(f"Error al buscar usuario: {e}")
        return None


def search_userPM(field: str, key):
    try:
        user = db_client.graduates.find_one({field: key})
        if user:
            return UserPM(**user_schemaPM(user))
        else:
            return None  # Si no se encuentra el usuario, devolver None
    except Exception as e:
        print(f"Error al buscar usuario: {e}")
        return None


async def search_fusion_user(id: str, db: Session = Depends(get_db)):
    try:
        user_mongo = search_userPM("id", id)
    except Exception as e:
        print(f"Error al buscar usuario en MongoDB: {e}")
        user_mongo = None

    try:
        postgres_user = (
            db.query(EgresadoBasico).filter(EgresadoBasico.id_egre == id).one()
        )
        user_postgres = postgres_user_schema(postgres_user)
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Egresado no encontrado")

    # Fusionar los datos de usuario de ambas fuentes en un nuevo diccionario
    merged_user = {}
    if user_mongo:
        merged_user.update(user_mongo)
    if user_postgres:
        merged_user.update(user_postgres)

    return merged_user


async def search_user_admin(field: str, key):
    try:
        user = db_client.admins.find_one({field: key})
        if user:
            return User(**user_schema(user))
        else:
            return None  # Si no se encuentra el usuario, devolver None
    except Exception as e:
        print(f"Error al buscar usuario: {e}")
        return None
