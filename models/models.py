from pydantic import BaseModel, Field
from datetime import date, datetime
from sqlalchemy import JSON, Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from typing import Dict, Optional

Base = declarative_base()

# Modelos para interactuar con postgre
class EgresadoBasico(Base):
    __tablename__ = 'egresado_basico'

    id_egre = Column(String, primary_key=True)
    id_carrera = Column(String)
    modalidad = Column(String)
    id_especialidad = Column(String)
    periodo_egreso = Column(String)
    nombre = Column(JSON)
    edad = Column(String)
    curp = Column(String)
    sexo = Column(String)
    telefono = Column(JSON)
    correo = Column(JSON)
    direccion = Column(JSON)

class AdministrativoBasico(Base):
    __tablename__ = 'administrativo_basico'

    id_adm = Column(String, primary_key=True)
    nombre = Column(String)
    cargo = Column(String)
    fecha_nacimiento = Column(Date)
    genero = Column(String)
    direccion = Column(JSON)
    correo = Column(JSON)
    telefono = Column(JSON)

class UserDB(Base):
    __tablename__ = 'usuarios'

    id_user = Column(String, primary_key=True)
    tipo = Column(String)
    correo = Column(String)


class EgresadoUpdate(BaseModel):
    id_carrera: str = Field(default="ISIC-2010-224", description="ID de la carrera")
    modalidad: str = Field(default="presencial", description="Modalidad")
    id_especialidad: str = Field(default="ISIE-CEN-2022-02", description="ID de la especialidad")
    periodo_egreso: str = Field(default=f"Agosto-Diciembre {datetime.today().year}", description="Periodo de Egreso")
    nombre: Dict[str, str] = Field(..., description="Nombre")
    edad: str = Field(default="25", description="Edad")
    curp: str = Field(..., description="CURP")
    sexo: str = Field(default="Hombre", description="Sexo")
    telefono: Dict[str, str] = Field(..., description="Telefono del Egresado")
    correo: Dict[str, str] = Field(..., description="Email del Egresado")
    direccion: Dict[str, str] = Field(..., description="Direccion del Egresado")

class AdministrativoUpdate(BaseModel):
    nombre: str = Field(..., description="Nombre")
    cargo: str = Field(..., description="Cargo")
    fecha_nacimiento: date = Field(..., description="Cargo")
    genero: str = Field(default="Hombre", description="Genero")
    direccion: Dict[str, str] = Field(..., description="Direccion del Egresado")
    correo: Dict[str, str] = Field(..., description="Correo del Egresado")
    telefono: Dict[str, str] = Field(..., description="Telefono del Egresado")