from pydantic import BaseModel
from datetime import date
from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from typing import Optional

Base = declarative_base()

class Egresado(Base):
    __tablename__ = 'egresado_basico'

    id_egre = Column(String, primary_key=True)
    id_carrera = Column(String)
    modalidad = Column(String)
    id_especialidad = Column(String)
    curp = Column(String)
    nombre = Column(String)
    apellidos = Column(String)
    fecha_egreso = Column(Date)

class EgresadoUpdate(BaseModel):
    id_carrera: Optional[str] = None
    modalidad: Optional[str] = None
    id_especialidad: Optional[str] = None
    curp: Optional[str] = None
    nombre: Optional[str] = None
    apellidos: Optional[str] = None
    fecha_egreso: Optional[date] = None