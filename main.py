from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class name(BaseModel):
    nombre: str
    apellido: str


# Ruta principal
@app.get("/")
def read_root():
    return {"mensaje": "Hola desde tu API FastAPI desplegada en Railway"}


# Ruta de saludo por parámetro en la URL
@app.get("/saludo/{nombre}")
def saludo(nombre: str):
    return {"saludo": f"Hola, {nombre}!"}

# Ruta de saludo usando JSON con nombre y apellido
@app.post("/saludo")
def saludo_personalizado(name: Name):
    return {"saludo": f"Hola, {name.nombre} {name.apellido}!"}