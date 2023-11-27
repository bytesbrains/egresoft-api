from models.models import CarreraDB, EspecialidadDB, PlanEstudioDB


def user_schema(user) -> dict:
    return {
        "id": user["id"],
        "email": user["email"],
        "disabled": user["disabled"],
        "password": user.get("password", ""),
        "role": user.get("role", None),
    }


def users_schema(users) -> list:
    return [user_schema(user) for user in users]


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
