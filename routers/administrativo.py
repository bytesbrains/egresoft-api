from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import SQLAlchemyError
from models.models import AdministrativoBasico,AdministrativoUpdate,Base
from database.database import engine,get_db
from sqlalchemy.orm import Session
from utils.helper_functions import get_administrativo

Base.metadata.create_all(bind=engine)

router = APIRouter(prefix='/administrativo', tags={'administrativo'}, responses={404: {"message": "No encontrado"}})

@router.get('/get/{id_adm}')
async def return_administrativo(id_adm: str, db: Session = Depends(get_db)):
    try:
        return db.query(AdministrativoBasico).filter(AdministrativoBasico.id_adm == id_adm).one()
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Administrativo no encontrado")
    
@router.put("/{id_adm}")
async def actualizar_administrativo(id_adm: str, updated_data: AdministrativoUpdate, db: Session = Depends(get_db)):
    try:
        admin_actual = await get_administrativo(db, id_adm)

        # Actualiza solo los datos ingresados
        for key, value in updated_data.dict(exclude_unset=True).items():
            setattr(admin_actual, key, value)

        db.commit()
        return {"message": "Datos del administrativo actualizados correctamente"}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error interno del servidor")
    finally:
        db.close()
