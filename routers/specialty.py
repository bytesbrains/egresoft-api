from fastapi import APIRouter, Depends, HTTPException
from models.models import Base, EspecialidadDB, Especialidad
from database.database import engine, get_db
from sqlalchemy.orm import Session
from typing import List
from schemas.user import especialidad_schema, especialidades_schema

Base.metadata.create_all(bind=engine)

router = APIRouter(
    prefix="/specialty",
    tags={"specialty"},
    responses={404: {"message": "No encontrado"}},
)


@router.get("/get/specialties", response_model=List[Especialidad])
async def get_all_especialidades(db: Session = Depends(get_db)):
    return especialidades_schema(db.query(EspecialidadDB).all())


@router.get("/get/specialty/{especialidad_id}", response_model=Especialidad)
async def get_especialidad(especialidad_id: str, db: Session = Depends(get_db)):
    especialidad = (
        db.query(EspecialidadDB)
        .filter(EspecialidadDB.id_especialidad == especialidad_id)
        .first()
    )
    if not especialidad:
        raise HTTPException(status_code=404, detail="Especialidad no encontrada")

    return especialidad_schema(especialidad)


@router.post("/add/specialty", response_model=Especialidad)
async def add_especialidad(especialidad: Especialidad, db: Session = Depends(get_db)):
    try:
        especialidad_data = EspecialidadDB(
            id_especialidad=especialidad.id_especialidad,
            nombre=especialidad.nombre,
        )
        db.add(especialidad_data)
        db.commit()
        db.refresh(especialidad_data)
        added_data = especialidad_data.__dict__
        added_data.pop("_sa_instance_state", None)
        return added_data
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error al agregar especialidad: {str(e)}"
        )
    finally:
        db.close()


@router.put("/update/specialty/{especialidad_id}", response_model=Especialidad)
async def update_especialidad(
    especialidad_id: str, especialidad: Especialidad, db: Session = Depends(get_db)
):
    existing_especialidad = (
        db.query(EspecialidadDB)
        .filter(EspecialidadDB.id_especialidad == especialidad_id)
        .first()
    )
    if not existing_especialidad:
        raise HTTPException(status_code=404, detail="Especialidad no encontrada")

    try:
        for attr, value in especialidad.dict().items():
            setattr(existing_especialidad, attr, value)

        db.add(existing_especialidad)
        db.commit()
        db.refresh(existing_especialidad)
        updated_data = existing_especialidad.__dict__
        updated_data.pop("_sa_instance_state", None)
        return updated_data
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error al actualizar especialidad: {str(e)}"
        )
    finally:
        db.close()
