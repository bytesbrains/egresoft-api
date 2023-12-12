from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models.models import EgresadoBasico, CarreraDB
from database.database import get_db

router = APIRouter(prefix='/dashboard', tags={'dashboard'}, responses={404: {"message": "No encontrado"}})

@router.get("/get/graduates")
async def get_graduates(db: Session = Depends(get_db)):
    try:
        # Realizar una consulta para obtener los datos requeridos
        egresados_data = (
            db.query(
                EgresadoBasico.id_egre,
                EgresadoBasico.nombre,
                EgresadoBasico.curp,
                CarreraDB.nombre.label("carrera_nombre"),
                EgresadoBasico.periodo_egreso
            )
            .join(CarreraDB, (EgresadoBasico.id_carrera == CarreraDB.id_carrera) &
                  (EgresadoBasico.modalidad == CarreraDB.modalidad))
            .all()
        )

        # Verificar si hay resultados
        if not egresados_data:
            raise HTTPException(status_code=404, detail="No se encontraron egresados")

        # Formatear los resultados si es necesario
        formatted_egresados = [
            {
                "id_egre": egresado.id_egre,
                "nombre": egresado.nombre,
                "curp": egresado.curp,
                "carrera_nombre": egresado.carrera_nombre,
                "periodo_egreso": egresado.periodo_egreso,
            }
            for egresado in egresados_data
        ]

        return formatted_egresados

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error en la base de datos: {str(e)}")
