from fastapi import APIRouter, Depends, HTTPException
from models.models import CarreraDB, CarrerAdd, Base
from database.database import engine, get_db
from sqlalchemy.orm import Session
from typing import List
from schemas.user import carrera_schema, carreras_schema


Base.metadata.create_all(bind=engine)

router = APIRouter(
    prefix="/careers", tags={"careers"}, responses={404: {"message": "No encontrado"}}
)


@router.get("/get/careers", response_model=List[CarrerAdd])
async def get_all_carreras(db: Session = Depends(get_db)):
    return carreras_schema(db.query(CarreraDB).all())


@router.get("/get/career/{carrera_id}")
async def get_carrera(carrera_id: str, db: Session = Depends(get_db)):
    carrera = db.query(CarreraDB).filter(CarreraDB.id_carrera == carrera_id).first()
    if not carrera:
        raise HTTPException(status_code=404, detail="Carrera no encontrada")

    return carrera_schema(carrera)


# Endpoint POST para agregar una carrera
@router.post("/add/career")
async def add_carrera(carrera: CarrerAdd, db: Session = Depends(get_db)):
    try:
        carrera_data = CarreraDB(
            id_carrera=carrera.id_carrera,
            modalidad=carrera.modalidad,
            nombre=carrera.nombre,
            jefe_dpt=carrera.jefe_dpt,
            cordinador=carrera.cordinador,
            evaluador=carrera.evaluador,
        )
        db.add(carrera_data)
        db.commit()
        db.refresh(carrera_data)
        added_data = carrera_data.__dict__
        added_data.pop("_sa_instance_state", None)
        return added_data
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error al agregar carrera: {str(e)}"
        )
    finally:
        db.close()


@router.put("/update/career/{carrera_id}")
async def update_carrera(
    carrera_id: str, carrera: CarrerAdd, db: Session = Depends(get_db)
):
    existing_carrera = (
        db.query(CarreraDB).filter(CarreraDB.id_carrera == carrera_id).first()
    )
    if not existing_carrera:
        raise HTTPException(status_code=404, detail="Carrera no encontrada")

    try:
        for attr, value in carrera.dict().items():
            setattr(existing_carrera, attr, value)

        db.add(existing_carrera)
        db.commit()
        db.refresh(existing_carrera)
        updated_data = existing_carrera.__dict__
        updated_data.pop("_sa_instance_state", None)
        return updated_data
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error al actualizar carrera: {str(e)}"
        )
    finally:
        db.close()
