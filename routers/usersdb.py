from fastapi import APIRouter, HTTPException, status
from fastapi import Depends
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from database.database import get_db, engine
from models.models import (
    AdministrativoBasico,
    AdministrativoUpdate,
    EgresadoBasico,
    EgresadoUpdate,
    UserDB,
    Base,
)
from models.userdb import User, hash_password, UserRole
from schemas.user import postgres_administrativo_schema, postgres_user_schema, user_schema
from database.client import db_client
from utils.helper_functions import get_administrativo, get_egresado, get_users, get_users_admin
from utils.usersdb import search_fusion_user_admin, search_user, search_user_admin, search_fusion_user

Base.metadata.create_all(bind=engine)

router = APIRouter(
    prefix="/usersdb",
    tags=["usersdb"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "No encontrado"}},
)


@router.get("/get/graduates")
async def users_graduates(db: Session = Depends(get_db)):
    try:
        # Obtener todos los egresados de MongoDB
        all_users_mongo = await get_users()

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
            merged_user.update({
                "id": all_users_mongo[i]["id"],
                "email": all_users_mongo[i]["email"],
                "disabled": all_users_mongo[i]["disabled"],
                "role": all_users_mongo[i]["role"]
            })

        if i < len(all_users_postgres):
            merged_user.update({
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
                "direccion": all_users_postgres[i]["direccion"]
            })

        merged_users.append(merged_user)

    return merged_users

@router.get("/get/graduate/{id}")
async def user(id: str, db: Session = Depends(get_db)):
    return search_fusion_user(id, db)


@router.post("/add/users", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: User, egresado_data: EgresadoUpdate, db: Session = Depends(get_db)
):
    existing_user = search_user("id", user.id)
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un usuario con ese ID",
        )

    existing_user = search_user("email", user.email)
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electrónico ya está en uso en otra cuenta",
        )

    hashed_password = hash_password(user.password)  # Utiliza la función hash_password
    user_dict = dict(user)
    user_dict[
        "hashed_password"
    ] = hashed_password  # Almacena la versión cifrada de la contraseña
    del user_dict["password"]  # Elimina la contraseña sin cifrar antes de la inserción
    user_dict["password"] = hashed_password
    # Elimina la contraseña que se uso para cifrar y solo se muestra el campo password y no hash_password
    del user_dict["hashed_password"]

    if user.role != UserRole.graduate:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se permite el rol a 'graduate'",
        )

    # Verifica que el valor de role sea válido antes de asignarlo al diccionario
    if user.role and not UserRole.__members__.get(user.role):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El valor de 'role' no es válido",
        )
    user_dict["role"] = (
        user.role if user.role else UserRole.graduate
    )  # Establece un valor predeterminado si no se proporciona

    user_id_mongo = db_client.graduates.insert_one(user_dict).inserted_id
    new_user_mongo = user_schema(db_client.graduates.find_one({"_id": user_id_mongo}))

    # Crear un nuevo usuario para PostgreSQL
    user_postgres = UserDB(
        id_user=user.id,
        tipo=user.role,
        correo=user.email,
    )

    # Insertar el nuevo usuario en PostgreSQL
    db.add(user_postgres)
    db.commit()

    # Insertar los datos en EgresadoBasico
    egresado_data_dict = egresado_data.dict()
    egresado_data_dict["id_egre"] = user.id  # Assuming user.id is the id_egre value

    egresado_instance = EgresadoBasico(**egresado_data_dict)
    db.add(egresado_instance)
    db.commit()
    db.close()

    return User(**new_user_mongo)


@router.put("/update/graduate", response_model=User)
async def update_user(user: User):
    existing_user = search_user("id", user.id)

    if existing_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado o no existente",
        )

    existing_user = search_user("email", user.email)

    if existing_user is not None and existing_user.id != user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electrónico ya está en uso en otra cuenta",
        )

    hashed_password = hash_password(user.password)  # Utiliza la función hash_password
    user_dict = dict(user)
    user_dict[
        "hashed_password"
    ] = hashed_password  # Almacena la versión cifrada de la contraseña
    del user_dict["password"]  # Elimina la contraseña sin cifrar antes de la inserción
    user_dict["password"] = hashed_password
    # Elimina la contraseña que se uso para cifrar y solo se muestra el campo password y no hash_password
    del user_dict["hashed_password"]

    if user.role != UserRole.graduate:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se permite actualizar el rol a 'graduate'",
        )

    try:
        db_client.graduates.find_one_and_replace({"id": user.id}, user_dict)
    except:
        return {"error": "No se ha actualizado el usuario"}

    return search_user("id", user.id)

@router.put("/update/graduate/{id_egre}")
async def update_postgres_graduate(id_egre: str, graduate_data: EgresadoUpdate, db: Session = Depends(get_db)):
    try:
        egresado_actual = await get_egresado(db, id_egre)

        # Update only the fields provided in the updated data
        for key, value in graduate_data.dict(exclude_unset=True).items():
            setattr(egresado_actual, key, value)

        db.commit()
        return {"message": "Datos del egresado actualizados correctamente"}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error interno del servidor")
    finally:
        db.close()

@router.delete("/delete/graduate/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def del_user(id: str, db: Session = Depends(get_db)):
    try:
        # Obtener el usuario a eliminar de MongoDB
        user_to_delete_mongo = db_client.graduates.find_one({"id": id})
        if not user_to_delete_mongo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado o no existente",
            )

        # Eliminar el usuario de MongoDB
        result_mongo = db_client.graduates.delete_one({"id": id})
        if result_mongo.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No se ha eliminado el usuario en MongoDB",
            )

        # Eliminar el usuario correspondiente en PostgreSQL
        user_to_delete_postgres = db.query(UserDB).filter(UserDB.id_user == id).first()
        if user_to_delete_postgres:
            db.delete(user_to_delete_postgres)
            db.commit()

    except Exception as e:
        print(f"Error al eliminar usuario: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ha ocurrido un error al eliminar el usuario",
        )


### Apartir de aqui todo es admin ###
@router.get("/get/admins")
async def users_admin(db: Session = Depends(get_db)):
    try:
        # Obtener todos los admins de MongoDB
        all_users_mongo = await get_users_admin()

    except Exception as e:
        print(f"Error al obtener todos los admins en MongoDB: {e}")
        all_users_mongo = []

    try:
        # Obtener todos los admins de PostgreSQL
        all_users_postgres = db.query(AdministrativoBasico).all()
        all_users_postgres = [postgres_administrativo_schema(user) for user in all_users_postgres]

    except Exception as e:
        print(f"Error al obtener todos los admins en PostgreSQL: {e}")
        all_users_postgres = []

    # Fusionar los datos de todos los admins de ambas fuentes de manera intercalada
    merged_users = []
    max_length = max(len(all_users_mongo), len(all_users_postgres))

    for i in range(max_length):
        merged_user = {}

        if i < len(all_users_mongo):
            merged_user.update({
                "id": all_users_mongo[i]["id"],
                "email": all_users_mongo[i]["email"],
                "disabled": all_users_mongo[i]["disabled"],
                "role": all_users_mongo[i]["role"]
            })

        if i < len(all_users_postgres):
            merged_user.update({
                "nombre": all_users_postgres[i]["nombre"],
                "cargo": all_users_postgres[i]["cargo"],
                "fecha_nacimiento": all_users_postgres[i]["fecha_nacimiento"],
                "genero": all_users_postgres[i]["genero"],
                "direccion": all_users_postgres[i]["direccion"],
                "correo": all_users_postgres[i]["correo"],
                "telefono": all_users_postgres[i]["telefono"]
            })

        merged_users.append(merged_user)

    return merged_users

@router.get("/get/admin/{id}")
async def user_admin(id: str, db: Session = Depends(get_db)):
    return search_fusion_user_admin(id, db)


@router.post("/add/admin", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user_admin(
    user: User, admin_data: AdministrativoUpdate, db: Session = Depends(get_db)
):
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

    hashed_password = hash_password(user.password)  # Utiliza la función hash_password
    user_dict = dict(user)
    user_dict[
        "hashed_password"
    ] = hashed_password  # Almacena la versión cifrada de la contraseña
    del user_dict["password"]  # Elimina la contraseña sin cifrar antes de la inserción
    user_dict["password"] = hashed_password
    # Elimina la contraseña que se uso para cifrar y solo se muestra el campo password y no hash_password
    del user_dict["hashed_password"]

    if user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se permite el rol a 'admin'",
        )
    # Verifica que el valor de role sea válido antes de asignarlo al diccionario
    if user.role and not UserRole.__members__.get(user.role):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El valor de 'role' no es válido",
        )
    user_dict["role"] = (
        user.role if user.role else UserRole.admin
    )  # Establece un valor predeterminado si no se proporciona

    user_id = db_client.admins.insert_one(user_dict).inserted_id

    new_user = user_schema(db_client.admins.find_one({"_id": user_id}))

    # Create a new user for PostgreSQL
    user_postgres = UserDB(
        id_user=user.id,
        tipo=user.role,
        correo=user.email,
    )

    # Insert the new user into PostgreSQL
    db.add(user_postgres)
    db.commit()

    # Insert data into AdministrativoBasico
    admin_data_dict = admin_data.dict()
    admin_data_dict["id_adm"] = user.id  # Assuming user.id is the id_egre value

    admin_instance = AdministrativoBasico(**admin_data_dict)
    db.add(admin_instance)
    db.commit()
    db.close()

    return User(**new_user)


@router.put("/update/admin", response_model=User)
async def update_user_admin(user: User):
    existing_user = search_user_admin("id", user.id)

    if existing_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado o no existente",
        )

    existing_user = search_user_admin("email", user.email)

    if existing_user is not None and existing_user.id != user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electrónico ya está en uso en otra cuenta",
        )

    hashed_password = hash_password(user.password)  # Utiliza la función hash_password
    user_dict = dict(user)
    user_dict[
        "hashed_password"
    ] = hashed_password  # Almacena la versión cifrada de la contraseña
    del user_dict["password"]  # Elimina la contraseña sin cifrar antes de la inserción
    user_dict["password"] = hashed_password
    # Elimina la contraseña que se uso para cifrar y solo se muestra el campo password y no hash_password
    del user_dict["hashed_password"]

    if user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se permite actualizar el rol a 'admin'",
        )

    try:
        db_client.admins.find_one_and_replace({"id": user.id}, user_dict)
    except:
        return {"error": "No se ha actualizado el usuario"}

    return search_user_admin("id", user.id)

@router.put("/update/admin/{id_adm}")
async def update_postgres_admin(id_adm: str, admin_data: AdministrativoUpdate, db: Session = Depends(get_db)):
    try:
        admin_actual = await get_administrativo(db, id_adm)

        # Update only the fields provided in the updated data
        for key, value in admin_data.dict(exclude_unset=True).items():
            setattr(admin_actual, key, value)

        db.commit()
        return {"message": "Datos del administrativo actualizados correctamente"}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error interno del servidor")
    finally:
        db.close()

@router.delete("/delete/admin/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def del_user_admin(id: str, db: Session = Depends(get_db)):
    try:
        user_to_delete = db_client.admins.find_one({"id": id})
        if not user_to_delete:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado o no existente",
            )

        result = db_client.admins.delete_one({"id": id})
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No se ha eliminado el usuario",
            )

        # Eliminar el usuario correspondiente en PostgreSQL
        user_to_delete = db.query(UserDB).filter(UserDB.id_user == id).first()
        if user_to_delete:
            db.delete(user_to_delete)
            db.commit()

    except Exception as e:
        print(f"Error al eliminar usuario: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ha ocurrido un error al eliminar el usuario o Usuario no encontrado / existente",
        )