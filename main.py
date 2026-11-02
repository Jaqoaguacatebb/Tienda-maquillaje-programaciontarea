import asyncio
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="API Proyecto Tiendita")

# Permite que el cliente (index.html) abierto desde el navegador consuma la API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cerrojo para sincronización asíncrona
lock = asyncio.Lock()

# Inventario simulado en memoria
# Rimel (ID 3) inicia con cantidad = 1 para simular la contención de la venta relámpago
inventario = [
    {"id": 1, "nombre": "Rubor", "precio": 200, "cantidad": 50},
    {"id": 2, "nombre": "Labial mate", "precio": 100, "cantidad": 30},
    {"id": 3, "nombre": "Rimel", "precio": 50, "cantidad": 1},  # Crítico
    {"id": 4, "nombre": "Protector solar", "precio": 400, "cantidad": 40},
    {"id": 5, "nombre": "Delineador negro", "precio": 100, "cantidad": 80},
    {"id": 6, "nombre": "Sombras", "precio": 250, "cantidad": 10},
]
siguiente_id = 7


class ProductoNuevo(BaseModel):
    nombre: str = Field(min_length=1)
    precio: float = Field(gt=0)
    cantidad: int = Field(ge=0)


@app.get("/")
async def raiz():
    return {"mensaje": "API Proyecto Tiendita funcionando"}


@app.get("/productos")
async def listar_productos():
    return inventario


@app.get("/productos/{producto_id}")
async def obtener_producto(producto_id: int):
    for objeto in inventario:
        if objeto["id"] == producto_id:
            return objeto
    raise HTTPException(status.HTTP_404_NOT_FOUND, "Producto no existe")


# ---------------- SECCIÓN CRÍTICA: COMPRA ----------------
@app.post("/productos/{producto_id}")
async def comprar_producto(producto_id: int):
    try:
        async with lock:  # Punto de control del experimento
            for objeto in inventario:
                if objeto["id"] == producto_id:
                    if objeto["cantidad"] > 0:
                        await asyncio.sleep(0.05)  # Latencia simulada de BD
                        objeto["cantidad"] -= 1
                        return {"mensaje": "Producto comprado"}
                    else:
                        raise HTTPException(400, "No hay stock")
            raise HTTPException(400, "Producto no existe")
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(500, f"Error interno: {str(error)}")


# ---------------- GESTIÓN DE STOCK ----------------
@app.post("/productos", status_code=status.HTTP_201_CREATED)
async def crear_producto(nuevo: ProductoNuevo):
    global siguiente_id
    async with lock:
        producto = {"id": siguiente_id, **nuevo.model_dump()}
        siguiente_id += 1
        inventario.append(producto)
    return producto


@app.delete("/productos/{producto_id}")
async def eliminar_producto(producto_id: int):
    async with lock:
        for i, objeto in enumerate(inventario):
            if objeto["id"] == producto_id:
                inventario.pop(i)
                return {"mensaje": f"Producto {producto_id} eliminado"}
    raise HTTPException(status.HTTP_404_NOT_FOUND, "Producto no existe")
