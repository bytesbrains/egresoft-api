from fastapi import HTTPException
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import Session
from models.models import EgresadoBasico

def get_egresado(db: Session, id_egre: str):
    try:
        return db.query(EgresadoBasico).filter(EgresadoBasico.id_egre == id_egre).one()
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Egresado no encontrado")