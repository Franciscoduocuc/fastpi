from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Hola desde tu API FastAPI desplegada en Railway"}

@app.get("/saludo/{nombre}")
def saludo(nombre: str):
    return {"saludo": f"Hola, {nombre}!"}