from dotenv import load_dotenv
from fastapi import FastAPI
from routers import user,egresado
from routers import user,usersdb

load_dotenv()

app = FastAPI()

app.include_router(user.router)
app.include_router(egresado.router)
app.include_router(user.router)
app.include_router(usersdb.router)

@app.get("/")
def read_root():
    return {"message": "¡Hola, mundo!"}

