from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import SQLAlchemyError
from models.models import EgresadoBasico, EgresadoUpdate, Base
from database.database import engine, get_db
from sqlalchemy.orm import Session
from utils.helper_functions import get_egresado

Base.metadata.create_all(bind=engine)

router = APIRouter(
    prefix="/egresado", tags={"egresado"}, responses={404: {"message": "No encontrado"}}
)


@router.get("/get/{id_egre}")
async def return_egresado(id_egre: str, db: Session = Depends(get_db)):
    try:
        return db.query(EgresadoBasico).filter(EgresadoBasico.id_egre == id_egre).one()
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Egresado no encontrado")


@router.put("/{id_egre}")
async def actualizar_egresado(
    id_egre: str, updated_data: EgresadoUpdate, db: Session = Depends(get_db)
):
    try:
        egresado_actual = await get_egresado(db, id_egre)

        # Update only the fields provided in the updated data
        for key, value in updated_data.dict(exclude_unset=True).items():
            setattr(egresado_actual, key, value)

        db.commit()
        return {"message": "Datos del egresado actualizados correctamente"}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error interno del servidor")
    finally:
        db.close()
