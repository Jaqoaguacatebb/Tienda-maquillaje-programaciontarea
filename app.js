const API = "http://127.0.0.1:8000";

const tabla = document.getElementById("tabla");
const estado = document.getElementById("estado");

function mostrarMensaje(texto, esError = false) {
  estado.textContent = texto;
  estado.className = "mensaje " + (esError ? "error" : "ok");
}

async function cargarProductos() {
  try {
    const respuesta = await fetch(`${API}/productos`);
    const productos = await respuesta.json();
    tabla.innerHTML = "";
    productos.forEach((p) => {
      const fila = document.createElement("tr");
      fila.innerHTML = `
        <td>${p.id}</td>
        <td>${p.nombre}</td>
        <td>$${p.precio}</td>
        <td class="${p.cantidad <= 0 ? "agotado" : ""}">${p.cantidad}</td>
        <td>
          <button onclick="comprar(${p.id})">Comprar</button>
          <button class="peligro" onclick="eliminar(${p.id})">Eliminar</button>
        </td>`;
      tabla.appendChild(fila);
    });
  } catch (e) {
    mostrarMensaje("No se pudo conectar con la API. ¿Está corriendo uvicorn?", true);
  }
}

async function comprar(id) {
  const respuesta = await fetch(`${API}/productos/${id}`, { method: "POST" });
  const datos = await respuesta.json();
  if (respuesta.ok) {
    mostrarMensaje(datos.mensaje);
  } else {
    mostrarMensaje(`Error ${respuesta.status}: ${datos.detail}`, true);
  }
  cargarProductos();
}

async function eliminar(id) {
  const respuesta = await fetch(`${API}/productos/${id}`, { method: "DELETE" });
  const datos = await respuesta.json();
  mostrarMensaje(respuesta.ok ? datos.mensaje : `Error ${respuesta.status}: ${datos.detail}`, !respuesta.ok);
  cargarProductos();
}

document.getElementById("formulario").addEventListener("submit", async (evento) => {
  evento.preventDefault();
  const cuerpo = {
    nombre: document.getElementById("nombre").value,
    precio: parseFloat(document.getElementById("precio").value),
    cantidad: parseInt(document.getElementById("cantidad").value, 10),
  };
  const respuesta = await fetch(`${API}/productos`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(cuerpo),
  });
  if (respuesta.ok) {
    mostrarMensaje("Producto agregado");
    evento.target.reset();
  } else {
    mostrarMensaje("No se pudo agregar el producto", true);
  }
  cargarProductos();
});

cargarProductos();
