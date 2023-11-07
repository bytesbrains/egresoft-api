from dotenv import load_dotenv
from fastapi import FastAPI
from routers import user

# Cargar variables de entorno desde el archivo .env
load_dotenv()

app = FastAPI()

app.include_router(user.router)


@app.get("/")
def read_root():
    return {"message": "¡Hola, mundo!"}
