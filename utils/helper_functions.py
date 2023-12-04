from fastapi import APIRouter, HTTPException,status
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import Session
from models.models import EgresadoBasico,AdministrativoBasico
from models.userdb import User
from schemas.user import users_schema
from database.client import db_client

router = APIRouter(
    prefix="/helper",
    tags=["helper"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "No encontrado"}},
)

@router.get("/get/graduates", response_model=list[User])
async def get_users():
    return users_schema(db_client.graduates.find())

@router.get("/get/admins", response_model=list[User])
async def get_users_admin():
    return users_schema(db_client.admins.find())

async def get_egresado(db: Session, id_egre: str):
    try:
        return db.query(EgresadoBasico).filter(EgresadoBasico.id_egre == id_egre).one()
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Egresado no encontrado")
    
async def get_administrativo(db: Session, id_adm: str):
    try:
        return db.query(AdministrativoBasico).filter(AdministrativoBasico.id_adm == id_adm).one()
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Administrativo no encontrado")