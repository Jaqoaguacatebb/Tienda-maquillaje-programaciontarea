from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


inventario = [
    {"id": 1, "nombre": "Rubor", "precio": 200, "cantidad": 50},
    {"id": 2, "nombre": "Labial mate", "precio": 100, "cantidad": 30},
    {"id": 3, "nombre": "Rimel", "precio": 50, "cantidad": 20},
    {"id": 4, "nombre": "Protector solar", "precio": 400, "cantidad": 40},
    {"id": 5, "nombre": "Delineador negro", "precio": 100, "cantidad": 80},
    {"id": 6, "nombre": "Sombras", "precio": 250, "cantidad": 10}
]


@app.get("/")
def home():
    return {"Message": "Hola bienvenido"}

@app.get("/productos")
def getProductos():
    return inventario

@app.post("/productos")
def addProducto(producto: dict):

    nuevo_id = len(inventario) + 1
    nuevo_producto = {
        "id": nuevo_id,    
        "nombre": producto["nombre"],
        "precio": producto["precio"],
        "cantidad": producto["cantidad"]
    }

    inventario.append(nuevo_producto)

    return inventario

@app.delete("/productos/{producto_id}")
def deleteProducto(producto_id: int):
    for producto in inventario:
        if producto["id"] == producto_id:
            inventario.remove(producto)
            return {"Message": "El producto fue eliminado"}
    return {"Message": "No fue encontrado el producto"}


