from models.models import (
    CarreraDB,
    AdministrativoBasico,
    EspecialidadDB,
    PlanEstudioDB,
    EgresadoBasico,
    EmpleadoBasico,
)


def user_schema(user) -> dict:
    return {
        "id": user["id"],
        "email": user["email"],
        "disabled": user["disabled"],
        "password": user.get("password", ""),
        "role": user.get("role", None),
    }


def user_schemaPM(user) -> dict:
    return {
        "id": user["id"],
        "email": user["email"],
        "disabled": user["disabled"],
        "password": user.get("password", ""),
        "role": user.get("role", None),
    }


def users_schema(users) -> list:
    return [user_schema(user) for user in users]


# Schema para datos de usuario en PostgreSQL
def postgres_user_schema(user: EgresadoBasico) -> dict:
    return {
        "id_carrera": user.id_carrera,
        "modalidad": user.modalidad,
        "id_especialidad": user.id_especialidad,
        "periodo_egreso": user.periodo_egreso,
        "nombre": user.nombre,
        "edad": user.edad,
        "curp": user.curp,
        "sexo": user.sexo,
        "telefono": user.telefono,
        "correo": user.correo,
        "direccion": user.direccion,
        # Aquí puedes agregar más campos si es necesario # "id": user.id_egre, en caso de querrer retornar algo mas
    }


def postgres_administrativo_schema(admin: AdministrativoBasico) -> dict:
    return {
        "nombre": admin.nombre,
        "cargo": admin.cargo,
        "fecha_nacimiento": admin.fecha_nacimiento,
        "genero": admin.genero,
        "direccion": admin.direccion,
        "correo": admin.correo,
        "telefono": admin.telefono,
    }


def carrera_schema(carrera: CarreraDB) -> dict:
    return {
        "id_carrera": carrera.id_carrera,
        "modalidad": carrera.modalidad,
        "nombre": carrera.nombre,
        "jefe_dpt": carrera.jefe_dpt,
        "cordinador": carrera.cordinador,
        "evaluador": carrera.evaluador,
    }


def carreras_schema(carreras: list[CarreraDB]) -> list[dict]:
    return [carrera_schema(carrera) for carrera in carreras]


def especialidad_schema(especialidad: EspecialidadDB) -> dict:
    return {
        "id_especialidad": especialidad.id_especialidad,
        "nombre": especialidad.nombre,
    }


def especialidades_schema(especialidades: list[EspecialidadDB]) -> list[dict]:
    return [especialidad_schema(especialidad) for especialidad in especialidades]


def plan_estudio_schema(plan_estudio: PlanEstudioDB) -> dict:
    return {
        "id_carrera": plan_estudio.id_carrera,
        "modalidad": plan_estudio.modalidad,
        "id_especialidad": plan_estudio.id_especialidad,
        "periodo": plan_estudio.periodo,
    }


def planes_estudio_schema(planes_estudio: list[PlanEstudioDB]) -> list[dict]:
    return [plan_estudio_schema(plan) for plan in planes_estudio]


def empleador_schema(empleado: EmpleadoBasico) -> dict:
    return {
        "id_emp": empleado.id_emp,
        "nombre_empresa": empleado.nombre_empresa,
        "nombre_responsable": empleado.nombre_responsable,
        "cargo_responsable": empleado.cargo_responsable,
        "direccion": empleado.direccion.model_dump() if empleado.direccion else None,
        "correo": empleado.correo.model_dump() if empleado.correo else None,
        "telefono": empleado.telefono.model_dump() if empleado.telefono else None,
        "detalle": empleado.detalle,
    }
