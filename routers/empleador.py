from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import SQLAlchemyError
from models.models import Base, EmpleadorBasico, EmpleadoBasico
from database.database import engine, get_db
from sqlalchemy.orm import Session
from utils.helper_functions import get_empleador

Base.metadata.create_all(bind=engine)

router = APIRouter(
    prefix="/empleador",
    tags={"Empleador"},
    responses={404: {"message": "No encontrado"}},
)


@router.get("/get/{id_emp}")
async def return_empleador(id_emp: str, db: Session = Depends(get_db)):
    try:
        return db.query(EmpleadorBasico).filter(EmpleadorBasico.id_emp == id_emp).one()
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Empleador no encontrado")


@router.put("/{id_emp}")
async def actualizar_empleador(
    id_emp: str, updated_data: EmpleadoBasico, db: Session = Depends(get_db)
):
    try:
        empleador_actual = await get_empleador(db, id_emp)

        # Actualiza solo los datos ingresados
        for key, value in updated_data.dict(exclude_unset=True).items():
            setattr(empleador_actual, key, value)

        db.commit()
        return {"message": "Datos del Empleador actualizados correctamente"}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error interno del servidor")
    finally:
        db.close()
