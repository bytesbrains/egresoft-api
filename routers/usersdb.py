from fastapi import APIRouter, HTTPException, status
from models.userdb import User, hash_password
from schemas.user import user_schema,users_schema
from database.client import db_client
from utils.usersdb import search_user
from bcrypt import hashpw, gensalt
from bson import ObjectId



router = APIRouter(prefix="/userdb",tags=["userdb"],responses={status.HTTP_404_NOT_FOUND: {"message": "No encontrado"}})


@router.get("/", response_model=list[User])
async def users():
    return users_schema(db_client.users.find())


@router.get("/{id}")  # Path
async def user(id: str):
    return search_user("_id", ObjectId(id))



@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user: User):
    existing_user = search_user("email", user.email)
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario con este correo electrónico ya existe",
        )

    hashed_password = hash_password(user.password)  # Utiliza la función hash_password
    user_dict = dict(user)
    user_dict["hashed_password"] = hashed_password  # Almacena la versión cifrada de la contraseña
    del user_dict["id"]
    del user_dict["password"]  # Elimina la contraseña sin cifrar antes de la inserción
    user_dict["password"] = hashed_password
    del user_dict["hashed_password"]  # Elimina la contraseña que se uso para cifrar y solo se muestra el campo password y no hash_password
    
    id = db_client.users.insert_one(user_dict).inserted_id

    new_user = user_schema(db_client.users.find_one({"_id": id}))

    return User(**new_user)


@router.put("/", response_model=User)
async def update_user(user: User):

    user_dict = dict(user)
    del user_dict["id"]

    try:
        db_client.users.find_one_and_replace(
            {"_id": ObjectId(user.id)}, user_dict)
    except:
        return {"error": "No se ha actualizado el usuario"}

    return search_user("_id", ObjectId(user.id))


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def del_user(id: str):

    found = db_client.users.find_one_and_delete({"_id": ObjectId(id)})

    if not found:
        return {"error": "No se ha eliminado el usuario"}
