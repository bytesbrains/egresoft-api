from pydantic import BaseModel, Field
from datetime import date, datetime
from sqlalchemy import (
    JSON,
    Column,
    Integer,
    String,
    Date,
    PrimaryKeyConstraint,
    ForeignKeyConstraint,
    CheckConstraint,
)
from sqlalchemy.ext.declarative import declarative_base
from typing import Dict, Optional
from enum import Enum
from sqlalchemy.orm import relationship

Base = declarative_base()


# Campos JSON
class Nombre(BaseModel):
    nombre: Optional[str]
    apellido_paterno: Optional[str]
    apellido_materno: Optional[str]


class Telefono(BaseModel):
    telefono_personal: Optional[str]
    telefono_trabajo: Optional[str]


class Correo(BaseModel):
    correo_personal: Optional[str]
    correo_trabajo: Optional[str]


class Direccion(BaseModel):
    Direccion_1: Optional[str]
    Direccion_2: Optional[str]
    Direccion_3: Optional[str]


# Modelos para interactuar con postgre
class EgresadoBasico(Base):
    __tablename__ = "egresado_basico"

    id_egre = Column(String, primary_key=True)
    id_carrera = Column(String, nullable=True)  # Campo opcional
    modalidad = Column(String, nullable=True)  # Campo opcional
    id_especialidad = Column(String, nullable=True)  # Campo opcional
    periodo_egreso = Column(String, nullable=True)  # Campo opcional
    nombre = Column(JSON, nullable=True)  # Campo opcional
    edad = Column(String, nullable=True)  # Campo opcional
    curp = Column(String, nullable=True)  # Campo obligatorio
    sexo = Column(String, nullable=True)  # Campo opcional
    telefono = Column(JSON, nullable=True)  # Campo opcional
    correo = Column(JSON, nullable=True)  # Campo opcional
    direccion = Column(JSON, nullable=True)  # Campo opcional


class AdministrativoBasico(Base):
    __tablename__ = "administrativo_basico"

    id_adm = Column(String, primary_key=True)
    nombre = Column(String, nullable=True)  # Campo opcional
    cargo = Column(String, nullable=True)  # Campo opcional
    fecha_nacimiento = Column(Date, nullable=True)  # Campo opcional
    genero = Column(String, nullable=True)  # Campo opcional
    direccion = Column(JSON, nullable=True)  # Campo opcional
    correo = Column(JSON, nullable=True)  # Campo opcional
    telefono = Column(JSON, nullable=True)  # Campo opcional


class UserDB(Base):
    __tablename__ = "usuarios"

    id_user = Column(String, primary_key=True)
    tipo = Column(String)
    correo = Column(String)


class CarreraDB(Base):
    __tablename__ = "carrera"

    id_carrera = Column(String, nullable=False)
    modalidad = Column(String, nullable=False)
    nombre = Column(String)
    jefe_dpt = Column(String)
    cordinador = Column(String)
    evaluador = Column(String)

    # Definir la clave primaria compuesta
    __table_args__ = (PrimaryKeyConstraint("id_carrera", "modalidad"),)


class EgresadoUpdate(BaseModel):
    id_carrera: Optional[str] = Field(
        default="ISIC-2010-224", description="ID de la carrera"
    )
    modalidad: Optional[str] = Field(default="presencial", description="Modalidad")
    id_especialidad: Optional[str] = Field(
        default="ISIE-CEN-2022-02", description="ID de la especialidad"
    )
    periodo_egreso: Optional[str] = Field(
        default=f"Agosto-Diciembre {datetime.today().year}",
        description="Periodo de Egreso",
    )
    nombre: Optional[Nombre] = None
    edad: Optional[str] = Field(default="25", description="Edad")
    curp: Optional[str] = Field(default="RXXXXXXXXXXXXXXXX2", description="")
    sexo: Optional[str] = Field(default="Hombre", description="Sexo")
    telefono: Optional[Telefono] = None
    correo: Optional[Correo] = None
    direccion: Optional[Direccion] = None


class AdministrativoUpdate(BaseModel):
    nombre: Optional[str] = Field(default="Nombre", description="Nombre")
    cargo: Optional[str] = Field(default="Cargo", description="Cargo")
    fecha_nacimiento: Optional[date] = Field(
        default=f"{datetime.today().date()}", description="Fecha de Nacimiento"
    )
    genero: Optional[str] = Field(default="Hombre", description="Genero")
    direccion: Optional[Direccion] = None
    correo: Optional[Correo] = None
    telefono: Optional[Telefono] = None


class Modalitype(str, Enum):
    presencial = "Presencial"
    distancia = "Distancia"


class CarrerAdd(BaseModel):
    id_carrera: Optional[str] = Field(
        default="ISIC-2010-224", description="ID de la carrera"
    )
    modalidad: Optional[str] = Field(default="Presencial", description="Modalidad")
    nombre: Optional[str] = None
    jefe_dpt: Optional[str] = None
    cordinador: Optional[str] = None
    evaluador: Optional[str] = None


class EspecialidadDB(Base):
    __tablename__ = "especialidad"

    id_especialidad = Column(String, nullable=False)
    nombre = Column(String)

    # Definir la clave primaria compuesta
    __table_args__ = (PrimaryKeyConstraint("id_especialidad"),)


class Especialidad(BaseModel):
    id_especialidad: Optional[str] = Field(
        default="ISIE-CEN-2022-02", description="ID de la especialidad"
    )
    nombre: Optional[str] = None


class PlanEstudioDB(Base):
    __tablename__ = "plan_estudio"

    id_carrera = Column(String, nullable=True)  # Campo opcional
    modalidad = Column(String, nullable=True)  # Campo opcional
    id_especialidad = Column(String, nullable=False)
    periodo = Column(String, nullable=False)

    # Clave primaria compuesta
    __table_args__ = (
        PrimaryKeyConstraint("id_carrera", "modalidad", "id_especialidad"),
        ForeignKeyConstraint(
            ["id_carrera", "modalidad"],
            ["carrera.id_carrera", "carrera.modalidad"],
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["id_especialidad"],
            ["especialidad.id_especialidad"],
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        CheckConstraint("id_carrera ~ '^[A-Z]{4}[-]20[0-9]{2}[-]2[0-9]{2}$'"),
        CheckConstraint("modalidad in ('presencial', 'distancia')"),
        CheckConstraint("periodo ~ '^[a-zA-Z]+[ -]+[a-zA-Z]+[ -]+[0-9]{4}$'"),
    )

    # Relaciones si es necesario (dependiendo de tu lógica de negocio)
    carrera = relationship("CarreraDB")
    especialidad = relationship("EspecialidadDB")


class PlanEstudio(BaseModel):
    id_carrera: Optional[str] = Field(default=None, description="ID de la carrera")
    modalidad: Optional[str] = Field(default=None, description="Modalidad")
    id_especialidad: str = Field(default=None, description="ID de la especialidad")
    periodo: Optional[str] = Field(
        default=f"Agosto-Diciembre {datetime.today().year}",
        description="Periodo",
    )

    class Config:
        from_attributes = True
