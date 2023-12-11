from fastapi import APIRouter, HTTPException, status
from fastapi import Depends
from sqlalchemy.orm import Session
from database.database import get_db, engine
from models.models import (
    AdministrativoBasico,
    AdministrativoUpdate,
    EgresadoBasico,
    EgresadoUpdate,
    EmpleadorBasico,
    Base,
)
from models.userdb import User, hash_password, UserRole
from schemas.user import (
    postgres_administrativo_schema,
    postgres_user_schema,
    user_schema,
    users_schema,
)
from database.client import db_client
from utils.usersdb import (
    search_user,
    search_user_admin,
    search_fusion_user_admin,
    search_fusion_user,
    search_user_employer,
    search_fusion_user_employer,
)

Base.metadata.create_all(bind=engine)

router = APIRouter(
    prefix="/usersdb",
    tags=["usersdb"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "No encontrado"}},
)


### Apartir de aqui todo es graduate ###
@router.get("/get/graduates")
async def users_graduates(db: Session = Depends(get_db)):
    try:
        # Obtener todos los egresados de MongoDB
        all_users_mongo = await users_schema(db_client.graduates.find())

    except Exception as e:
        print(f"Error al obtener todos los egresados en MongoDB: {e}")
        all_users_mongo = []

    try:
        # Obtener todos los egresados de PostgreSQL
        all_users_postgres = db.query(EgresadoBasico).all()
        all_users_postgres = [postgres_user_schema(user) for user in all_users_postgres]

    except Exception as e:
        print(f"Error al obtener todos los egresados en PostgreSQL: {e}")
        all_users_postgres = []

    # Fusionar los datos de todos los egresados de ambas fuentes de manera intercalada
    merged_users = []
    max_length = max(len(all_users_mongo), len(all_users_postgres))

    for i in range(max_length):
        merged_user = {}

        if i < len(all_users_mongo):
            merged_user.update(
                {
                    "id": all_users_mongo[i]["id"],
                    "email": all_users_mongo[i]["email"],
                    "disabled": all_users_mongo[i]["disabled"],
                    "role": all_users_mongo[i]["role"],
                }
            )

        if i < len(all_users_postgres):
            merged_user.update(
                {
                    "id_carrera": all_users_postgres[i]["id_carrera"],
                    "modalidad": all_users_postgres[i]["modalidad"],
                    "id_especialidad": all_users_postgres[i]["id_especialidad"],
                    "periodo_egreso": all_users_postgres[i]["periodo_egreso"],
                    "nombre": all_users_postgres[i]["nombre"],
                    "edad": all_users_postgres[i]["edad"],
                    "curp": all_users_postgres[i]["curp"],
                    "sexo": all_users_postgres[i]["sexo"],
                    "telefono": all_users_postgres[i]["telefono"],
                    "correo": all_users_postgres[i]["correo"],
                    "direccion": all_users_postgres[i]["direccion"],
                }
            )

        merged_users.append(merged_user)

    return merged_users


@router.get("/get/graduate/{id}")
async def user(id: str, db: Session = Depends(get_db)):
    return search_fusion_user(id, db)


@router.post("/add/graduate", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: User, egresado_data: EgresadoUpdate, db: Session = Depends(get_db)
):
    try:
        existing_user = search_user("id", user.id)
        if existing_user is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un usuario con ese ID",
            )

        hashed_password = hash_password(user.password)
        user_dict = dict(user)
        user_dict["hashed_password"] = hashed_password
        del user_dict["password"]
        user_dict["password"] = hashed_password

        if user.role != UserRole.graduate:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Solo se permite el rol a 'graduate'",
            )

        if user.role and not UserRole.__members__.get(user.role):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El valor de 'role' no es válido",
            )
        user_dict["role"] = user.role if user.role else UserRole.graduate

        user_id_mongo = db_client.graduates.insert_one(user_dict).inserted_id
        new_user_mongo = user_schema(
            db_client.graduates.find_one({"_id": user_id_mongo})
        )

        egresado_data_dict = egresado_data.dict()
        egresado_data_dict["id_egre"] = user.id

        egresado_instance = EgresadoBasico(**egresado_data_dict)
        db.add(egresado_instance)
        db.commit()
        db.close()

        return User(**new_user_mongo)

    except Exception as e:
        print(f"Error al crear el usuario: {e}")
        # Si ocurre un error, intenta eliminar el usuario creado de MongoDB
        try:
            result_mongo = db_client.graduates.delete_one({"_id": user_id_mongo})
            if result_mongo.deleted_count == 0:
                print("No se ha eliminado el usuario en MongoDB")

        except Exception as ex:
            print(f"Error al eliminar el usuario de MongoDB: {ex}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ha ocurrido un error al crear el usuario",
        )


### Apartir de aqui todo es admin ###
@router.get("/get/admins")
async def users_admin(db: Session = Depends(get_db)):
    try:
        # Obtener todos los admins de MongoDB
        all_users_mongo = users_schema(db_client.admins.find())

    except Exception as e:
        print(f"Error al obtener todos los admins en MongoDB: {e}")
        all_users_mongo = []

    try:
        # Obtener todos los admins de PostgreSQL
        all_users_postgres = db.query(AdministrativoBasico).all()
        all_users_postgres = [
            postgres_administrativo_schema(user) for user in all_users_postgres
        ]

    except Exception as e:
        print(f"Error al obtener todos los admins en PostgreSQL: {e}")
        all_users_postgres = []

    # Fusionar los datos de todos los admins de ambas fuentes de manera intercalada
    merged_users = []
    max_length = max(len(all_users_mongo), len(all_users_postgres))

    for i in range(max_length):
        merged_user = {}

        if i < len(all_users_mongo):
            merged_user.update(
                {
                    "id": all_users_mongo[i]["id"],
                    "email": all_users_mongo[i]["email"],
                    "disabled": all_users_mongo[i]["disabled"],
                    "role": all_users_mongo[i]["role"],
                }
            )

        if i < len(all_users_postgres):
            merged_user.update(
                {
                    "nombre": all_users_postgres[i]["nombre"],
                    "cargo": all_users_postgres[i]["cargo"],
                    "fecha_nacimiento": all_users_postgres[i]["fecha_nacimiento"],
                    "genero": all_users_postgres[i]["genero"],
                    "direccion": all_users_postgres[i]["direccion"],
                    "correo": all_users_postgres[i]["correo"],
                    "telefono": all_users_postgres[i]["telefono"],
                }
            )

        merged_users.append(merged_user)

    return merged_users


@router.get("/get/admin/{id}")  # Path
async def user_admin(id: str, db: Session = Depends(get_db)):
    return search_fusion_user_admin(id, db)


@router.post("/add/admin", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user_admin(
    user: User, admin_data: AdministrativoUpdate, db: Session = Depends(get_db)
):
    try:
        existing_user = search_user_admin("id", user.id)
        if existing_user is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un usuario con ese ID",
            )

        existing_user = search_user_admin("email", user.email)
        if existing_user is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El correo electrónico ya está en uso en otra cuenta",
            )

        hashed_password = hash_password(user.password)
        user_dict = dict(user)
        user_dict["hashed_password"] = hashed_password
        del user_dict["password"]
        user_dict["password"] = hashed_password

        if user.role != UserRole.admin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Solo se permite el rol a 'admin'",
            )

        if user.role and not UserRole.__members__.get(user.role):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El valor de 'role' no es válido",
            )
        user_dict["role"] = user.role if user.role else UserRole.admin

        user_id = db_client.admins.insert_one(user_dict).inserted_id

        new_user = user_schema(db_client.admins.find_one({"_id": user_id}))

        admin_data_dict = admin_data.dict()
        admin_data_dict["id_adm"] = user.id

        admin_instance = AdministrativoBasico(**admin_data_dict)
        db.add(admin_instance)
        db.commit()
        db.close()

        return User(**new_user)

    except Exception as e:
        print(f"Error al crear el usuario: {e}")
        # Si ocurre un error, intenta eliminar el usuario creado de MongoDB
        try:
            user_to_delete = db_client.admins.find_one({"id": user.id})
            if user_to_delete:
                result = db_client.admins.delete_one({"id": user.id})
                if result.deleted_count == 0:
                    print("No se ha eliminado el usuario de MongoDB")

        except Exception as ex:
            print(f"Error al eliminar el usuario de MongoDB: {ex}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ha ocurrido un error al crear el usuario",
        )


### Apartir de aqui todo de employer ###
@router.get("/get/employer/{id}")
async def user_employer(id: str, db: Session = Depends(get_db)):
    return search_fusion_user_employer(id, db)


@router.post("/add/employer", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user_employer(
    user: User, empleador_data: EgresadoUpdate, db: Session = Depends(get_db)
):
    try:
        existing_user = search_user_employer("id", user.id)
        if existing_user is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un usuario con ese ID",
            )

        hashed_password = hash_password(user.password)
        user_dict = dict(user)
        user_dict["hashed_password"] = hashed_password
        del user_dict["password"]
        user_dict["password"] = hashed_password

        if user.role != UserRole.employer:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Solo se permite el rol a 'employer'",
            )

        if user.role and not UserRole.__members__.get(user.role):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El valor de 'role' no es válido",
            )
        user_dict["role"] = user.role if user.role else UserRole.employer

        user_id_mongo = db_client.employers.insert_one(user_dict).inserted_id
        new_user_mongo = user_schema(
            db_client.employers.find_one({"_id": user_id_mongo})
        )

        empleador_data_dict = empleador_data.dict()
        empleador_data_dict["id_egre"] = user.id

        empleador_instance = EmpleadorBasico(**empleador_data_dict)
        db.add(empleador_instance)
        db.commit()
        db.close()

        return User(**new_user_mongo)

    except Exception as e:
        print(f"Error al crear el usuario: {e}")
        # Si ocurre un error, intenta eliminar el usuario creado de MongoDB
        try:
            result_mongo = db_client.employers.delete_one({"_id": user_id_mongo})
            if result_mongo.deleted_count == 0:
                print("No se ha eliminado el usuario en MongoDB")

        except Exception as ex:
            print(f"Error al eliminar el usuario de MongoDB: {ex}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ha ocurrido un error al crear el usuario",
        )
