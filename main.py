from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional, Literal
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

class Empleado(BaseModel):
    nombre: str
    puesto: str
    correo: str
    telefono: str
    fecha_ingreso: date

class SolicitudSoporte(BaseModel):
    cliente_id: str
    descripcion: str
    estado: Literal['pendiente', 'en_proceso', 'completado'] = 'pendiente'
    fecha_solicitud: Optional[date] = None
    fecha_solucion: Optional[date] = None
    observacion: Optional[str] = None
    empleado_id: Optional[str] = None

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

@app.get("/empleados", tags=["Empleado"])
async def obtener_todos_los_empleados():
    if not DATABASE_URL:
        raise HTTPException(status_code=500, detail="DATABASE_URL no está definida.")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{DATABASE_URL}/empleado.json")
            response.raise_for_status()
            datos = response.json()
            if not isinstance(datos, list):
                raise HTTPException(status_code=500, detail="La estructura no es una lista.")
            empleados = []
            for i, empleado in enumerate(datos):
                if empleado is not None:
                    if 'fecha_ingreso' in empleado:
                        try:
                            empleado['fecha_ingreso'] = datetime.strptime(empleado['fecha_ingreso'], "%Y-%m-%d").date()
                        except:
                            pass  # por si ya es date
                    empleados.append({"id": str(i), **empleado})
            return {"empleados": empleados}
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Error al conectar con Firebase: {str(e)}")

@app.get("/empleado/{empleado_id}", tags=["Empleado"])
async def obtener_empleado(empleado_id: str):
    if not DATABASE_URL:
        raise HTTPException(status_code=500, detail="DATABASE_URL no está definida.")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{DATABASE_URL}/empleado/{empleado_id}.json")
            if response.status_code != 200 or response.json() is None:
                raise HTTPException(status_code=404, detail="Empleado no encontrado.")
            datos = response.json()
            if 'fecha_ingreso' in datos:
                try:
                    datos['fecha_ingreso'] = datetime.strptime(datos['fecha_ingreso'], "%Y-%m-%d").date()
                except:
                    pass
            return {"empleado_id": empleado_id, "datos": datos}
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Error al conectar con Firebase: {str(e)}")

@app.post("/empleado/{empleado_id}", tags=["Empleado"])
async def agregar_empleado(empleado_id: str, empleado: Empleado):
    if not DATABASE_URL:
        raise HTTPException(status_code=500, detail="DATABASE_URL no está definida.")
    empleado_data = empleado.dict()
    empleado_data['fecha_ingreso'] = empleado_data['fecha_ingreso'].isoformat()
    try:
        async with httpx.AsyncClient() as client:
            check = await client.get(f"{DATABASE_URL}/empleado/{empleado_id}.json")
            if check.status_code == 200 and check.json() is not None:
                raise HTTPException(status_code=400, detail="El empleado ya existe.")
            response = await client.put(f"{DATABASE_URL}/empleado/{empleado_id}.json", json=empleado_data)
            response.raise_for_status()
            return {
                "mensaje": "Empleado agregado correctamente",
                "firebase_response": response.json()
            }
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Error al conectar con Firebase: {str(e)}")

@app.put("/empleado/{empleado_id}", tags=["Empleado"])
async def actualizar_empleado(empleado_id: str, empleado: Empleado):
    if not DATABASE_URL:
        raise HTTPException(status_code=500, detail="DATABASE_URL no está definida.")
    empleado_data = empleado.dict()
    empleado_data['fecha_ingreso'] = empleado_data['fecha_ingreso'].isoformat()
    try:
        async with httpx.AsyncClient() as client:
            check = await client.get(f"{DATABASE_URL}/empleado/{empleado_id}.json")
            if check.status_code != 200 or check.json() is None:
                raise HTTPException(status_code=404, detail="Empleado no encontrado.")
            response = await client.put(f"{DATABASE_URL}/empleado/{empleado_id}.json", json=empleado_data)
            response.raise_for_status()
            return {
                "mensaje": "Empleado actualizado correctamente",
                "firebase_response": response.json()
            }
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Error al conectar con Firebase: {str(e)}")

@app.delete("/empleado/{empleado_id}", tags=["Empleado"])
async def eliminar_empleado(empleado_id: str):
    if not DATABASE_URL:
        raise HTTPException(status_code=500, detail="DATABASE_URL no está definida.")
    try:
        async with httpx.AsyncClient() as client:
            check = await client.get(f"{DATABASE_URL}/empleado/{empleado_id}.json")
            if check.status_code != 200 or check.json() is None:
                raise HTTPException(status_code=404, detail="Empleado no encontrado.")
            response = await client.delete(f"{DATABASE_URL}/empleado/{empleado_id}.json")
            response.raise_for_status()
            return {
                "mensaje": f"Empleado {empleado_id} eliminado correctamente"
            }
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Error al conectar con Firebase: {str(e)}")

@app.get("/soportes", tags=["Soporte"])
async def obtener_todas_las_solicitudes_soporte():
    if not DATABASE_URL:
        raise HTTPException(status_code=500, detail="DATABASE_URL no está definida.")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{DATABASE_URL}/soporte.json")
            response.raise_for_status()
            datos = response.json()
            if not isinstance(datos, list):
                raise HTTPException(status_code=500, detail="La estructura no es una lista.")
            soportes = [
                {"id": str(i), **soporte}
                for i, soporte in enumerate(datos)
                if soporte is not None
            ]
            return {"soportes": soportes}
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Error al conectar con Firebase: {str(e)}")

@app.get("/soporte/{soporte_id}", tags=["Soporte"])
async def obtener_solicitud_soporte(soporte_id: str):
    if not DATABASE_URL:
        raise HTTPException(status_code=500, detail="DATABASE_URL no está definida.")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{DATABASE_URL}/soporte/{soporte_id}.json")
            if response.status_code != 200 or response.json() is None:
                raise HTTPException(status_code=404, detail="Solicitud de soporte no encontrada.")
            return {"soporte_id": soporte_id, "datos": response.json()}
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Error al conectar con Firebase: {str(e)}")

@app.post("/soporte/{soporte_id}", tags=["Soporte"])
async def crear_solicitud_soporte(soporte_id: str, solicitud: SolicitudSoporte):
    if not DATABASE_URL:
        raise HTTPException(status_code=500, detail="DATABASE_URL no está definida.")
    solicitud_data = solicitud.dict()
    for fecha in ["fecha_solicitud", "fecha_solucion"]:
        if solicitud_data.get(fecha):
            solicitud_data[fecha] = solicitud_data[fecha].isoformat()
    try:
        async with httpx.AsyncClient() as client:
            check_soporte = await client.get(f"{DATABASE_URL}/soporte/{soporte_id}.json")
            if check_soporte.status_code == 200 and check_soporte.json() is not None:
                raise HTTPException(status_code=400, detail="La solicitud de soporte ya existe.")
            cliente_resp = await client.get(f"{DATABASE_URL}/cliente/{solicitud.cliente_id}.json")
            if cliente_resp.status_code != 200 or cliente_resp.json() is None:
                raise HTTPException(status_code=404, detail="Cliente no encontrado.")
            if solicitud.empleado_id:
                empleado_resp = await client.get(f"{DATABASE_URL}/empleado/{solicitud.empleado_id}.json")
                if empleado_resp.status_code != 200 or empleado_resp.json() is None:
                    raise HTTPException(status_code=404, detail="Empleado no encontrado.")
            response = await client.put(f"{DATABASE_URL}/soporte/{soporte_id}.json", json=solicitud_data)
            response.raise_for_status()
            return {
                "mensaje": "Solicitud de soporte creada correctamente",
                "firebase_response": response.json()
            }
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Error al conectar con Firebase: {str(e)}")

@app.put("/soporte/{soporte_id}", tags=["Soporte"])
async def actualizar_solicitud_soporte(soporte_id: str, solicitud: SolicitudSoporte):
    if not DATABASE_URL:
        raise HTTPException(status_code=500, detail="DATABASE_URL no está definida.")
    solicitud_data = solicitud.dict()
    try:
        async with httpx.AsyncClient() as client:
            check = await client.get(f"{DATABASE_URL}/soporte/{soporte_id}.json")
            if check.status_code != 200 or check.json() is None:
                raise HTTPException(status_code=404, detail="Solicitud de soporte no encontrada.")
            # Si las fechas son proporcionadas, se deben convertir a formato ISO
            for fecha in ["fecha_solicitud", "fecha_solucion"]:
                if solicitud_data.get(fecha):
                    solicitud_data[fecha] = solicitud_data[fecha].isoformat()
            response = await client.put(f"{DATABASE_URL}/soporte/{soporte_id}.json", json=solicitud_data)
            response.raise_for_status()
            return {
                "mensaje": "Solicitud de soporte actualizada correctamente",
                "firebase_response": response.json()
            }
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Error al conectar con Firebase: {str(e)}")

@app.delete("/soporte/{soporte_id}", tags=["Soporte"])
async def eliminar_solicitud_soporte(soporte_id: str):
    if not DATABASE_URL:
        raise HTTPException(status_code=500, detail="DATABASE_URL no está definida.")
    try:
        async with httpx.AsyncClient() as client:
            check = await client.get(f"{DATABASE_URL}/soporte/{soporte_id}.json")
            if check.status_code != 200 or check.json() is None:
                raise HTTPException(status_code=404, detail="Solicitud de soporte no encontrada.")
            response = await client.delete(f"{DATABASE_URL}/soporte/{soporte_id}.json")
            response.raise_for_status()
            return {"mensaje": "Solicitud de soporte eliminada correctamente"}
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Error al conectar con Firebase: {str(e)}")