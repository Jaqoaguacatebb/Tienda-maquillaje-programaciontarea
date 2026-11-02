import json
from collections import Counter

from locust import HttpUser, task, between, events

# Contador de códigos HTTP de la compra (200 = comprado, 400 = sin stock)
codigos_compra = Counter()


@events.test_stop.add_listener
def mostrar_resumen(environment, **kwargs):
    print("\n=== RESUMEN COMPRAS POST /productos/3 ===")
    print(f"200 OK (compras exitosas):      {codigos_compra[200]}")
    print(f"400 Bad Request (sin stock):    {codigos_compra[400]}")
    otros = sum(v for k, v in codigos_compra.items() if k not in (200, 400))
    print(f"Otros (errores inesperados):    {otros}")
    with open("resumen_compras.json", "w") as f:
        json.dump({str(k): v for k, v in codigos_compra.items()}, f)


class UsuarioTienditaCompleto(HttpUser):
    wait_time = between(0.2, 0.8)

    # Escritura: venta relámpago sobre el producto crítico (Rimel, ID 3)
    @task(3)
    def comprarProducto(self):
        # catch_response=True: el agotamiento de stock (400) NO se cuenta como falla del sistema
        with self.client.post("/productos/3", catch_response=True) as respuesta:
            codigos_compra[respuesta.status_code] += 1
            if respuesta.status_code in (200, 400):
                respuesta.success()
            else:
                respuesta.failure(f"Error inesperado: {respuesta.status_code}")

    # Lectura: raíz de la API
    @task(1)
    def getProducto(self):
        self.client.get("/")

    # FUNCIÓN ADICIONAL requerida por el profesor: consulta del catálogo completo
    @task(2)
    def listarProductos(self):
        self.client.get("/productos")
