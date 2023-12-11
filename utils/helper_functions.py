from fastapi import HTTPException
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import Session
from models.models import EgresadoBasico, AdministrativoBasico, EmpleadorBasico


async def get_egresado(db: Session, id_egre: str):
    try:
        return db.query(EgresadoBasico).filter(EgresadoBasico.id_egre == id_egre).one()
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Egresado no encontrado")


async def get_administrativo(db: Session, id_adm: str):
    try:
        return (
            db.query(AdministrativoBasico)
            .filter(AdministrativoBasico.id_adm == id_adm)
            .one()
        )
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Administrativo no encontrado")


async def get_empleador(db: Session, id_emp: str):
    try:
        return db.query(EmpleadorBasico).filter(EmpleadorBasico.id_emp == id_emp).one()
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Empleador no encontrado")
