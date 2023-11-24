from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from models.models import EgresadoUpdate,Base
from database.database import engine,get_db
from sqlalchemy.orm import Session
from utils.helper_functions import get_egresado

Base.metadata.create_all(bind=engine)

router = APIRouter(prefix='/egresado', tags={'egresado'}, responses={404: {"message": "No encontrado"}})

@router.put("/{id_egre}")
def actualizar_egresado(id_egre: str, updated_data: EgresadoUpdate, db: Session = Depends(get_db)):
    try:
        egresado_actual = get_egresado(db, id_egre)

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
