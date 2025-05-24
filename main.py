from fastapi import FastAPI, Query, HTTPException, Body
import httpx
import os
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import stripe
from typing import List


class CarritoRequest(BaseModel):
    productos: List[str]  # Lista de IDs de productos

class ProductoCarrito(BaseModel):
    id: str
    nombre: str
    precio: float

class NovedadPayload(BaseModel):
    es_novedad: bool

class PaymentRequest(BaseModel):
    amount: int  # Monto en centavos (ej: 1000 = $10.00)
    currency: str = "usd"
    payment_method_id: str

novedades = {}

load_dotenv()

app = FastAPI()

stripe.api_key = os.getenv("STRIPE_API_KEY")
FERREMAS_API_URL = os.getenv("FERREMAS_API_URL")
FERREMAS_TOKEN = os.getenv("FERREMAS_TOKEN")

headers = {
    "x-authentication": FERREMAS_TOKEN  
}

@app.get("/")

# ✅ Obtener todos los productos
@app.get("/productos")
async def get_productos():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{FERREMAS_API_URL}/data/articulos", headers=headers)
        return response.json()


# ✅ Obtener un producto por ID
@app.get("/productos/{producto_id}")
async def get_producto(producto_id: str):
    async with httpx.AsyncClient() as client:
        external_url = f"{FERREMAS_API_URL}/data/articulos/{producto_id}"
        print(f"DEBUG: Llamando a API externa: GET {external_url}")
        print(f"DEBUG: Usando token (primeros 5 chars): {FERREMAS_TOKEN[:5] if FERREMAS_TOKEN else 'None'}...")

        response = await client.get(external_url, headers=headers)

        print(f"DEBUG: Respuesta de API externa - Status: {response.status_code}")
        # Es importante ver el texto de la respuesta, especialmente en errores
        print(f"DEBUG: Respuesta de API externa - Texto: {response.text}")

        if response.status_code == 200:
            try:
                return response.json()
            except Exception as e:
                print(f"DEBUG: Error al parsear JSON de API externa: {e}")
                return JSONResponse(
                    content={
                        "error": "Error al procesar la respuesta JSON de la API externa.",
                        "external_status_code": response.status_code,
                        "external_response_text": response.text # Devuelve el texto original si no es JSON
                    },
                    status_code=500 # Error interno de tu API porque no pudo procesar
                )
        else:
            return JSONResponse(
                content={
                    "error": "Producto no encontrado o error en la API externa.",
                    "producto_id_solicitado": producto_id,
                    "external_api_status_code": response.status_code,
                    "external_api_response_text": response.text # Muy útil para saber qué dijo la API externa
                },
                status_code=response.status_code # Puedes usar el mismo status o uno propio (e.g. 400, 404, 502)
            )



# ✅ Obtener todas las sucursales
@app.get("/sucursales")
async def get_sucursales():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{FERREMAS_API_URL}/data/sucursales", headers=headers)
        return response.json()

# ✅ Obtener una sucursal por ID
@app.get("/sucursales/{sucursal_id}")
async def get_sucursal(sucursal_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{FERREMAS_API_URL}/data/sucursales/{sucursal_id}", headers=headers)
        return response.json()

# ✅ Obtener todos los vendedores
@app.get("/vendedores")
async def get_vendedores():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{FERREMAS_API_URL}/data/vendedores", headers=headers)
        return response.json()

# ✅ Obtener un vendedor por ID
@app.get("/vendedores/{vendedor_id}")
async def get_vendedor(vendedor_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{FERREMAS_API_URL}/data/vendedores/{vendedor_id}", headers=headers)
        return response.json()

@app.get("/sucursales_con_vendedores")
async def get_sucursales_con_vendedores():
    async with httpx.AsyncClient() as client:
        sucursales_resp = await client.get(f"{FERREMAS_API_URL}/data/sucursales", headers=headers)
        vendedores_resp = await client.get(f"{FERREMAS_API_URL}/data/vendedores", headers=headers)
        sucursales = sucursales_resp.json()
        vendedores = vendedores_resp.json()
        return [
            {
                "id_sucursal": s["id"],
                "localidad": s["localidad"],
                "id_vendedor": v["id"],
                "nombre": v["nombre"],
                "email": v["email"]
            }
            for v in vendedores
            for s in sucursales
            if s["id"] == v["sucursal"]
        ]

@app.put("/productos/{producto_id}/marcar_novedad")
async def marcar_novedad(producto_id: str, payload: NovedadPayload): # Cambiado aquí
    if payload.es_novedad: # Usar payload.es_novedad
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{FERREMAS_API_URL}/data/articulos/{producto_id}", headers=headers)
            if response.status_code == 200:
                data = response.json()
                novedades[producto_id] = {
                    "id": data.get("id", producto_id),
                    "nombre": data.get("nombre", f"Producto {producto_id}")
                }
                return {"mensaje": f"Producto {producto_id} marcado como novedad"}
            else:
                return JSONResponse(content={"error": "Producto no encontrado en la API"}, status_code=404)
    else:
        if producto_id in novedades:
            del novedades[producto_id]
        return {"mensaje": f"Producto {producto_id} desmarcado como novedad"}

@app.get("/productos/novedades")
async def obtener_novedades():
    print(f"OBTENER NOVEDADES - Tipo de 'novedades': {type(novedades)}")
    print(f"OBTENER NOVEDADES - Contenido de 'novedades': {novedades}")
    try:
        # Intenta convertir los valores a una lista
        values_list = list(novedades.values())
        print(f"OBTENER NOVEDADES - Tipo de 'values_list': {type(values_list)}")
        print(f"OBTENER NOVEDADES - Contenido de 'values_list': {values_list}")

        # Verifica la serializabilidad de cada ítem individualmente (opcional pero útil para debug)
        for i, item in enumerate(values_list):
            try:
                json.dumps(item) # Intenta serializar el ítem
            except TypeError as e_serialize:
                print(f"OBTENER NOVEDADES - Error: Ítem {i} no es serializable JSON: {item}, Detalle: {e_serialize}")
                # Podrías devolver un error aquí si un ítem específico es el problema
                # return JSONResponse(content={"error": f"Ítem {i} no es serializable: {str(e_serialize)}"}, status_code=500)


        # Si todo parece bien, intenta devolver la respuesta
        return JSONResponse(content=values_list)

    except Exception as e:
        # Captura cualquier excepción que ocurra al procesar o devolver novedades
        print(f"OBTENER NOVEDADES - ERROR INESPERADO: {e}")
        import traceback
        traceback.print_exc() # Imprime el traceback completo en la consola del servidor
        return JSONResponse(
            content={"error": "Error interno del servidor al obtener novedades.", "detalle": str(e)},
            status_code=500
        )

@app.get("/conversion_dinero")
async def cambio_clp_usd(
    origen: str = Query(..., description="Divisa de origen: CLP o USD"),
    cantidad: float = Query(..., description="Cantidad a convertir")
):
    origen = origen.upper()
    if origen not in ["CLP", "USD"]:
        return JSONResponse(status_code=400, content={"error": "Solo se permite CLP o USD como divisa de origen"})

    url = "https://api.exchangerate-api.com/v4/latest/USD"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code != 200:
            return JSONResponse(status_code=500, content={"error": "No se pudo obtener la tasa de cambio"})

        tasas = response.json().get("rates", {})
        tasa_clp = tasas.get("CLP")
        if not tasa_clp:
            return JSONResponse(status_code=500, content={"error": "No se encontró la tasa para CLP"})

    if origen == "USD":
        resultado = cantidad * tasa_clp
        destino = "CLP"
    else:  # origen == "CLP"
        resultado = cantidad / tasa_clp
        destino = "USD"

    return {
        "origen": origen,
        "destino": destino,
        "cantidad": cantidad,
        "resultado": round(resultado, 2),
        "tasa_CLP_USD": tasa_clp
    }


@app.post("/carrito")
async def obtener_carrito(request: CarritoRequest = Body(...)):
    carrito_detalle = []
    async with httpx.AsyncClient() as client:
        for producto_id in request.productos:
            response = await client.get(f"{FERREMAS_API_URL}/data/articulos/{producto_id}", headers=headers)
            if response.status_code == 200:
                data = response.json()
                carrito_detalle.append({
                    "id": data.get("id", producto_id),
                    "nombre": data.get("nombre", "Producto desconocido"),
                    "precio": data.get("precio", 0)  # Ajusta la clave según tu API
                })
            else:
                carrito_detalle.append({
                    "id": producto_id,
                    "nombre": "Producto no encontrado",
                    "precio": 0
                })
    return {"carrito": carrito_detalle}

@app.post("/crear_pago")
async def crear_pago():
    intent = stripe.PaymentIntent.create(
        amount=1000,  # Monto en centavos (ejemplo: 1000 CLP = $10.00)
        currency="clp",
        payment_method_types=["card"],
    )
    return JSONResponse({"client_secret": intent.client_secret})