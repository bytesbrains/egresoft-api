from fastapi import APIRouter, Depends, HTTPException
from models.models import Base, PlanEstudioDB, PlanEstudio
from database.database import engine, get_db
from sqlalchemy.orm import Session
from typing import List
from schemas.user import plan_estudio_schema, planes_estudio_schema

Base.metadata.create_all(bind=engine)

router = APIRouter(
    prefix="/study_plan",
    tags={"study_plan"},
    responses={404: {"message": "No encontrado"}},
)


@router.get("/get/study_plans", response_model=List[PlanEstudio])
async def get_all_planes_estudio(db: Session = Depends(get_db)):
    return planes_estudio_schema(db.query(PlanEstudioDB).all())


@router.post("/add/study_plan", response_model=PlanEstudio)
async def add_plan_estudio(plan_estudio: PlanEstudio, db: Session = Depends(get_db)):
    try:
        plan_estudio_data = PlanEstudioDB(
            id_carrera=plan_estudio.id_carrera,
            modalidad=plan_estudio.modalidad,
            id_especialidad=plan_estudio.id_especialidad,
            periodo=plan_estudio.periodo,
        )
        db.add(plan_estudio_data)
        db.commit()
        db.refresh(plan_estudio_data)
        added_data = plan_estudio_data.__dict__
        added_data.pop("_sa_instance_state", None)
        return added_data
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error al agregar plan de estudio: {str(e)}"
        )
    finally:
        db.close()


@router.put("/update/study_plan/{plan_id}", response_model=PlanEstudio)
async def update_plan_estudio(
    plan_id: str, plan_estudio: PlanEstudio, db: Session = Depends(get_db)
):
    existing_plan_estudio = (
        db.query(PlanEstudioDB).filter(PlanEstudioDB.id_especialidad == plan_id).first()
    )
    if not existing_plan_estudio:
        raise HTTPException(status_code=404, detail="Plan de estudio no encontrado")

    try:
        for attr, value in plan_estudio.dict().items():
            setattr(existing_plan_estudio, attr, value)

        db.add(existing_plan_estudio)
        db.commit()
        db.refresh(existing_plan_estudio)
        updated_data = existing_plan_estudio.__dict__
        updated_data.pop("_sa_instance_state", None)
        return updated_data
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error al actualizar plan de estudio: {str(e)}"
        )
    finally:
        db.close()
