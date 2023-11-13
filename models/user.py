from pydantic import BaseModel,Field
class User(BaseModel):
    id: str
    username: str
    full_name: str
    email: str
    disabled: bool

class UserDB(User):
    password: str
