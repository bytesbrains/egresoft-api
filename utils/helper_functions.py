from fastapi import HTTPException
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import Session
from models.models import EgresadoBasico,AdministrativoBasico

async def get_egresado(db: Session, id_egre: str):
    try:
        return db.query(EgresadoBasico).filter(EgresadoBasico.id_egre == id_egre).one()
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Egresado no encontrado")
    
async def get_administrador(db: Session, id_adm: str):
    try:
        return db.query(AdministrativoBasico).filter(AdministrativoBasico.id_adm == id_adm).one()
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Administrador no encontrado")