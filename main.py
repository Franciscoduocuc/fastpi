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
    url_vendedores = "https://ea2p2assets-production.up.railway.app/data/vendedores"

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            # Solicitud a sucursales
            response_suc = await client.get(url_sucursales, headers=headers)
            response_suc.raise_for_status()
            sucursales = response_suc.json()

            # Solicitud a vendedores
            response_ven = await client.get(url_vendedores, headers=headers)
            response_ven.raise_for_status()
            vendedores = response_ven.json()


        # Opcional: Puedes procesar o filtrar datos aquí si quieres
        # Por ejemplo, solo devolver nombre y vendedores

        sucursales_con_vendedores = []
        for vendedor in vendedores:
            sucursal = next((s for s in sucursales if s["id"] == vendedor["sucursal"]), None)
            if sucursal:
                sucursales_con_vendedores.append({
                    "id_sucursal": sucursal["id"],
                    "localidad": sucursal["localidad"],
                    "id_vendedor": vendedor["id"],
                    "nombre": vendedor["nombre"],
                    "email": vendedor["email"]
                    })

        return sucursales_con_vendedores




    except httpx.HTTPStatusError as e:
        return {"error": f"HTTP error: {e.response.status_code}"}
    except Exception as e:
        return {"error": str(e)}