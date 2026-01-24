//Obtengo datos
import { apiFetch } from "./api.js";

const params = new URLSearchParams(window.location.search);
const id = params.get("id");

if (!id) {
    console.error("ID de informe no proporcionado");
    throw new Error("Falta ID de informe");
}

let informe = null;

async function cargarDetalle() {
    try {
        const response = await apiFetch(`/api/informes/${id}`);

        if (!response.ok) {
            throw new Error("Error al obtener informes del analisis");
        }

        informe = await response.json();

        mostrarDetalle(informe);

        if (informe.tipoAnalisis === "Dinamico") {
            await cargarDetalleOZ(informe.id);
        }

    } catch (error) {
        console.error(error);
    }
}

const severidadTexto = {
  1: "Baja",
  2: "Media",
  3: "Alta"
};

function mostrarDetalle(data) {
    document.getElementById("titulo").textContent = data.titulo;
    document.getElementById("nivel").textContent = severidadTexto[data.severidad] ?? "Desconocida";
    document.getElementById("nivel").classList.add(severidadTexto[data.severidad] ?? "Desconocida");

    document.getElementById("url").textContent = data.url;
    document.getElementById("url").href = data.url;
    document.getElementById("fecha").textContent = data.fechaAnalisis;
    document.getElementById("fuente").textContent = data.tipoAnalisis;

    document.getElementById("descripcion").textContent = data.descripcion;
    document.getElementById("impacto").textContent = data.impacto;
    document.getElementById("recomendacion").textContent = data.recomendacion;
    document.getElementById("evidencia").textContent = data.evidencia;

    if (data.codigo) {
        document.getElementById("codigo").textContent = data.codigo;
        document.getElementById("bloqueCodigo").hidden = false;
    }

}


async function cargarDetalleOZ(informeId) {
    try {
        const response = await apiFetch(`/api/detalle-oz/informe/${informeId}`);

        if (!response.ok) {
            return; // No hay detalle OZ → no mostramos nada
        }

        const oz = await response.json();

        mostrarDetalleOZ(oz);

    } catch (error) {
        console.error("Error al cargar detalle OZ", error);
    }
}


function mostrarDetalleOZ(oz) {
    const bloque = document.getElementById("bloqueDetalleOZ");

    let hayContenido = false;

    hayContenido |= setOZField("oz-endpoint", oz.endpoint);
    hayContenido |= setOZField("oz-metodo", oz.metodo);
    hayContenido |= setOZField("oz-parametro", oz.parametro);
    hayContenido |= setOZField("oz-payload", oz.payload);

    // Mostrar el bloque solo si hay al menos un dato técnico
    bloque.hidden = !hayContenido;
}


function setOZField(id, value) {
    const el = document.getElementById(id);
    const container = el.closest(".oz-item");

    if (!value || value.trim() === "") {
        container.classList.add("hidden");
        return false;
    }

    el.textContent = value;
    container.classList.remove("hidden");
    return true;
}





//Cargar los sitios al entrar
cargarDetalle()

//Volver a la lista de analisis
document.getElementById("btnVolver").addEventListener("click", (e) => {
    e.preventDefault();
    window.location.href = `/report-list?siteId=${informe.siteId}&analysisId=${informe.analisisId}`;
});