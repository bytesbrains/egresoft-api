from dotenv import load_dotenv
from fastapi import FastAPI
from routers import user, egresado, usersdb, administrativo, carrera

load_dotenv()

app = FastAPI()

app.include_router(user.router)
app.include_router(administrativo.router)
app.include_router(egresado.router)
app.include_router(usersdb.router)
app.include_router(carrera.router)


@app.get("/")
def read_root():
    return {"message": "¡Hola, mundo!"}
