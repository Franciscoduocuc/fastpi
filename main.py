from fastapi import FastAPI, HTTPException, Header
import httpx

app = FastAPI()


TOKEN = "SaGrP9ojGS39hU9ljqbXxQ=="

headers = {
    "x-authentication": TOKEN,
    "Accept": "application/json"
}

@app.get("/")
async def obtener_sucursales():
    url_sucursales = "https://ea2p2assets-production.up.railway.app/data/sucursales"

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            # Solicitud a sucursales
            response_suc = await client.get(url_sucursales, headers=headers)
            print("Status code sucursales:", response_suc.status_code)
            response_suc.raise_for_status()
            sucursales = response_suc.json()
            print("Datos sucursales:", sucursales)

        # Opcional: Puedes procesar o filtrar datos aquí si quieres
        # Por ejemplo, solo devolver nombre y vendedores

        resultado = []
        for suc in sucursales:
            resultado.append({
                "id": suc.get("id"),
                "localidad": suc.get("localidad")
            })

        return resultado

    except httpx.HTTPStatusError as e:
        return {"error": f"HTTP error: {e.response.status_code}"}
    except Exception as e:
        return {"error": str(e)}