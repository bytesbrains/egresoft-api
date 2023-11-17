from fastapi import APIRouter, HTTPException, status
from models.userdb import User, hash_password, UserRole
from schemas.user import user_schema, users_schema
from database.client import db_client
from utils.usersdb import search_user, search_user_admin
from bson import ObjectId


router = APIRouter(
    prefix="/userdb",
    tags=["userdb"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "No encontrado"}},
)


### Apartir de aqui todo es graduate ###
@router.get("/get/graduates", response_model=list[User])
async def users():
    return users_schema(db_client.graduates.find())


@router.get("/get/graduate/{id}")  # Path
async def user(id: str):
    return search_user("id", id)


@router.post("/add/graduate", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user: User):
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

    user_id = db_client.graduates.insert_one(user_dict).inserted_id

    new_user = user_schema(db_client.graduates.find_one({"_id": user_id}))

    return User(**new_user)


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


@router.delete("/delete/graduate/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def del_user(id: str):
    try:
        user_to_delete = db_client.graduates.find_one({"id": id})
        if not user_to_delete:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado o no existente",
            )

        result = db_client.graduates.delete_one({"id": id})
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No se ha eliminado el usuario",
            )
    except Exception as e:
        print(f"Error al eliminar usuario: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ha ocurrido un error al eliminar el usuario",
        )


### Apartir de aqui todo es admin ###
@router.get("/get/admins", response_model=list[User])
async def users_admin():
    return users_schema(db_client.admins.find())


@router.get("/get/admin/{id}")  # Path
async def user_admin(id: str):
    return search_user_admin("id", id)


@router.post("/add/admin", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user_admin(user: User):
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


@router.delete("/delete/admin/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def del_user_admin(id: str):
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
    except Exception as e:
        print(f"Error al eliminar usuario: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ha ocurrido un error al eliminar el usuario o Usuario no encontrado / existente",
        )
