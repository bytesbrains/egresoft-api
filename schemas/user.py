from models.models import CarreraDB, EspecialidadDB


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
