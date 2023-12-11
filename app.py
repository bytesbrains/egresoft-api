from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import (
    user,
    egresado,
    usersdb,
    administrativo,
    encuesta,
    career,
    specialty,
    study_plan,
    empleador,
)

load_dotenv()

app = FastAPI()

# Configurar los orígenes permitidos, métodos, encabezados, etc.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Reemplaza con los orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Rutas de tu aplicación FastAPI
@app.get("/")
async def read_root():
    return {"message": "Hello, World"}


app.include_router(user.router)
app.include_router(administrativo.router)
app.include_router(egresado.router)
app.include_router(empleador.router)
app.include_router(usersdb.router)
app.include_router(career.router)
app.include_router(specialty.router)
app.include_router(study_plan.router)
app.include_router(encuesta.router)
