from fastapi import FastAPI
from routers import jwt_auth_users
app = FastAPI()

app.include_router(jwt_auth_users.router)

@app.get("/")
def read_root():
    return {"message": "¡Hola, mundo!"}
