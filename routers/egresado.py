# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from database.database import get_db 
# from models.models import EgresadoUpdate
# from sqlalchemy import text


# router = APIRouter(prefix='/egresado',
#                    tags={'egresado'},
#                    responses={404: {"message": "No encontrado"}})


# @router.put("/{id_egre}")
# def actualizar_egresado(id_egre: str, updated_data: EgresadoUpdate, db: Session = Depends(get_db)):
#     try:
#         # Obtener datos actuales del egresado
#         select_query = text("""
#         SELECT id_carrera, modalidad, id_especialidad, curp, nombre, apellidos, fecha_egreso
#         FROM egresado_basico
#         WHERE id_egre = :id_egre
#         """)

#         result = db.execute(select_query, {"id_egre": id_egre})
#         egresado_actual = result.fetchone()

#         if not egresado_actual:
#             raise HTTPException(status_code=404, detail="Egresado no encontrado")

#         # Actualizar solo los campos proporcionados en los datos actualizados
#         id_carrera_actualizado = updated_data.id_carrera if updated_data.id_carrera else egresado_actual[0]
#         modalidad_actualizada = updated_data.modalidad if updated_data.modalidad else egresado_actual[1]
#         id_especialidad_actualizado = updated_data.id_especialidad if updated_data.id_especialidad else egresado_actual[2]
#         curp_actualizado = updated_data.curp if updated_data.curp else egresado_actual[3]
#         nombre_actualizado = updated_data.nombre if updated_data.nombre else egresado_actual[4]
#         apellidos_actualizados = updated_data.apellidos if updated_data.apellidos else egresado_actual[5]
#         fecha_egreso_actualizada = updated_data.fecha_egreso if updated_data.fecha_egreso else egresado_actual[6]

#         # Realizar la actualización
#         update_query = text("""
#         UPDATE egresado_basico
#         SET id_carrera = :id_carrera, modalidad = :modalidad, id_especialidad = :id_especialidad,
#             curp = :curp, nombre = :nombre, apellidos = :apellidos, fecha_egreso = :fecha_egreso
#         WHERE id_egre = :id_egre
#         """)

#         db.execute(
#             update_query,
#             {
#                 "id_egre": id_egre,
#                 "id_carrera": id_carrera_actualizado,
#                 "modalidad": modalidad_actualizada,
#                 "id_especialidad": id_especialidad_actualizado,
#                 "curp": curp_actualizado,
#                 "nombre": nombre_actualizado,
#                 "apellidos": apellidos_actualizados,
#                 "fecha_egreso": fecha_egreso_actualizada
#             }
#         )

#         db.commit()
#         db.close()

#         return {"message": "Datos del egresado actualizados correctamente"}
#     except Exception as e:
#         print(f"Error: {e}")
#         raise HTTPException(status_code=500, detail="Error interno del servidor")

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from models.models import EgresadoUpdate,Base
from database.database import engine,get_db
from sqlalchemy.orm import Session
from utils.egresado_functions import get_egresado

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
