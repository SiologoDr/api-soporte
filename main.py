from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
DATABASE_URL = os.getenv("DATABASE_URL")

class Cliente(BaseModel):
    nombre: str
    correo: str
    telefono: str
    direccion: str

@app.get("/clientes", tags=["Cliente"])
async def obtener_todos_los_clientes():
    if not DATABASE_URL:
        raise HTTPException(status_code=500, detail="DATABASE_URL no está definida.")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{DATABASE_URL}/cliente.json")
            response.raise_for_status()
            datos = response.json()
            if not isinstance(datos, list):
                raise HTTPException(status_code=500, detail="La estructura no es una lista.")
            clientes = [
                {"id": str(i), **cliente}
                for i, cliente in enumerate(datos)
                if cliente is not None
            ]
            return {"clientes": clientes}
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Error al conectar con Firebase: {str(e)}")

@app.get("/cliente/{cliente_id}", tags=["Cliente"])
async def obtener_cliente(cliente_id: str):
    if not DATABASE_URL:
        raise HTTPException(status_code=500, detail="DATABASE_URL no está definida.")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{DATABASE_URL}/cliente/{cliente_id}.json")
            if response.status_code != 200 or response.json() is None:
                raise HTTPException(status_code=404, detail="Cliente no encontrado.")
            return {"cliente_id": cliente_id, "datos": response.json()}
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Error al conectar con Firebase: {str(e)}")

@app.post("/cliente/{cliente_id}", tags=["Cliente"])
async def agregar_cliente(cliente_id: str, cliente: Cliente):
    if not DATABASE_URL:
        raise HTTPException(status_code=500, detail="DATABASE_URL no está definida.")
    cliente_data = cliente.dict()
    try:
        async with httpx.AsyncClient() as client:
            check = await client.get(f"{DATABASE_URL}/cliente/{cliente_id}.json")
            if check.status_code == 200 and check.json() is not None:
                raise HTTPException(status_code=400, detail="El cliente ya existe.")
            response = await client.put(f"{DATABASE_URL}/cliente/{cliente_id}.json", json=cliente_data)
            response.raise_for_status()
            return {
                "mensaje": "Cliente agregado correctamente",
                "firebase_response": response.json()
            }
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Error al conectar con Firebase: {str(e)}")
    
@app.put("/cliente/{cliente_id}", tags=["Cliente"])
async def actualizar_cliente(cliente_id: str, cliente: Cliente):
    if not DATABASE_URL:
        raise HTTPException(status_code=500, detail="DATABASE_URL no está definida.")
    try:
        async with httpx.AsyncClient() as client:
            check = await client.get(f"{DATABASE_URL}/cliente/{cliente_id}.json")
            if check.status_code != 200 or check.json() is None:
                raise HTTPException(status_code=404, detail="Cliente no encontrado.")
            response = await client.put(
                f"{DATABASE_URL}/cliente/{cliente_id}.json",
                json=cliente.dict()
            )
            response.raise_for_status()
            return {
                "mensaje": "Cliente actualizado correctamente",
                "firebase_response": response.json()
            }
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Error al conectar con Firebase: {str(e)}")

@app.delete("/cliente/{cliente_id}", tags=["Cliente"])
async def eliminar_cliente(cliente_id: str):
    if not DATABASE_URL:
        raise HTTPException(status_code=500, detail="DATABASE_URL no está definida.")
    try:
        async with httpx.AsyncClient() as client:
            check = await client.get(f"{DATABASE_URL}/cliente/{cliente_id}.json")
            if check.status_code != 200 or check.json() is None:
                raise HTTPException(status_code=404, detail="Cliente no encontrado.")
            response = await client.delete(f"{DATABASE_URL}/cliente/{cliente_id}.json")
            response.raise_for_status()
            return {
                "mensaje": f"Cliente {cliente_id} eliminado correctamente"
            }
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Error al conectar con Firebase: {str(e)}")