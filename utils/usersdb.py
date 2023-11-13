from models.userdb import User
from schemas.user import user_schema
from database.client import db_client


#si se usa un metodo, deben de estar abajo del todo que se uso
#get de usuarios con try catch
def search_user(field: str, key):
    try:
        user = db_client.users.find_one({field: key})
        if user:
            return User(**user_schema(user))
        else:
            return None  # Si no se encuentra el usuario, devolver None
    except Exception as e:
        print(f"Error al buscar usuario: {e}")
        return None
