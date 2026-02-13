//Obtengo datos
import { apiFetch } from "./api.js";
import { formatearFecha } from "./fecha.js";

//Obtengo el id de la URL
const params = new URLSearchParams(window.location.search);
const siteId = params.get("siteId");

let sitio = null;
let listaAnalisis = [];
let listaFiltrada = [];

// 🔹 Variables para mantener el orden actual
let ordenActual = null;      // columna actual
let ordenAscendente = true;  // dirección actual


async function cargarAnalisis() {
    try {
        const response = await apiFetch(`/api/sitios/${siteId}/detalle`);

        if (!response.ok) {
            throw new Error("Error al obtener analisis del sitio");
        }

        sitio = await response.json();

        document.getElementById("nombreSitio").textContent = sitio.nombre;
        document.getElementById("propietarioSitio").textContent = sitio.propietario;
        document.getElementById("urlSitio").textContent = sitio.url;

        listaAnalisis = sitio.analisis || [];
        listaFiltrada = [...listaAnalisis];

        document.getElementById("cantidadAnalisis").textContent = listaAnalisis.length;
        mostrarListado(listaFiltrada);

    } catch (error) {
        console.error(error);
    }
}

//Cargar los sitios al entrar
cargarAnalisis()




//Obtengo la tabla
const tablaAnalisis = document.querySelector("#tablaAnalisis tbody");

function mostrarListado(lista) {
    tablaAnalisis.innerHTML = ""; //Elimino los datos antiguos

    lista.forEach(item => {
        const tr = document.createElement("tr");

        tr.innerHTML = `
        <td>${item.tipo}</td>
        <td>${item.estado}</td>
        <td>${item.metodo}</td>
        <td>${item.resultado_global}</td>
        <td>${item.cantidad_informes}</td>
        <td>${formatearFecha(item.fecha)}</td>
        `;

        tr.style.cursor = "pointer";

        tr.addEventListener("click", () => {
            window.location.href = `/report-list?siteId=${siteId}&analysisId=${item.id}`;
        });

        tablaAnalisis.appendChild(tr);
    });
}


// 🔹 Función reutilizable para aplicar el orden actual
function aplicarOrden() {
    if (!ordenActual) return;

    listaFiltrada.sort((a, b) => {
        let A, B;

        switch (ordenActual) {
            case "fecha":
                A = new Date(a.fecha);
                B = new Date(b.fecha);
                break;

            case "resultado":
                A = Number(a.resultado_global);
                B = Number(b.resultado_global);
                break;

            case "vulnerabilidades":
                A = Number(a.cantidad_informes);
                B = Number(b.cantidad_informes);
                break;

            case "tipo":
                A = a.tipo?.toLowerCase();
                B = b.tipo?.toLowerCase();
                break;

            case "estado":
                A = a.estado?.toLowerCase();
                B = b.estado?.toLowerCase();
                break;

            case "metodo":
                A = a.metodo?.toLowerCase();
                B = b.metodo?.toLowerCase();
                break;

            default:
                return 0;
        }

        // 1️⃣ criterio principal
        if (A < B) return ordenAscendente ? -1 : 1;
        if (A > B) return ordenAscendente ? 1 : -1;

        // 2️⃣ desempate SIEMPRE por fecha DESC
        const fechaA = new Date(a.fecha);
        const fechaB = new Date(b.fecha);

        return fechaB - fechaA;
    });
}


const encabezados = document.querySelectorAll("#tablaAnalisis th.sortable");

encabezados.forEach(th => {
    th.addEventListener("click", () => {
        const columna = th.dataset.column;

        // 🔹 Determinar nueva dirección
        const asc = !th.classList.contains("asc");

        // 🔹 Guardar estado global
        ordenActual = columna;
        ordenAscendente = asc;

        // Resetear flechas
        encabezados.forEach(h => h.classList.remove("asc", "desc"));
        th.classList.add(asc ? "asc" : "desc");

        aplicarOrden();
        mostrarListado(listaFiltrada);
    });
});


//Filtros
const filtroTipo = document.getElementById("filtroTipo");
const filtroEstado = document.getElementById("filtroEstado");
const filtroMetodo = document.getElementById("filtroMetodo");
const filtroDesde = document.getElementById("filtroDesde");
const filtroHasta = document.getElementById("filtroHasta");

function aplicarFiltros() {
    const tipo = filtroTipo.value.toLowerCase().trim();
    const estado = filtroEstado.value.toLowerCase().trim();
    const metodo = filtroMetodo.value.toLowerCase().trim();
    const desde = filtroDesde.value ? new Date(filtroDesde.value) : null;
    const hasta = filtroHasta.value ? new Date(filtroHasta.value) : null;

    // Ajuste: incluir todo el día "hasta"
    if (hasta) {
        hasta.setHours(23, 59, 59, 999);
    }

    listaFiltrada = listaAnalisis.filter(item => {
        const coincideTipo =
            !tipo || item.tipo?.toLowerCase().trim() === tipo;

        const coincideEstado =
            !estado || item.estado?.toLowerCase().trim() === estado;

        const coincideMetodo =
            !metodo || item.metodo?.toLowerCase().trim() === metodo;

        const fechaItem = new Date(item.fecha);

        const coincideDesde =
            !desde || fechaItem >= desde;

        const coincideHasta =
            !hasta || fechaItem <= hasta;

        return coincideTipo && coincideEstado && coincideMetodo && coincideDesde && coincideHasta;
    });

    // 🔹 IMPORTANTE: reaplicar orden después del filtro
    aplicarOrden();
    mostrarListado(listaFiltrada);
}

// Eventos
filtroTipo.addEventListener("change", aplicarFiltros);
filtroEstado.addEventListener("change", aplicarFiltros);
filtroMetodo.addEventListener("change", aplicarFiltros);
filtroDesde.addEventListener("change", aplicarFiltros);
filtroHasta.addEventListener("change", aplicarFiltros);


//Limpiar filtros
document.getElementById("btnLimpiarFiltros").addEventListener("click", () => {
    filtroTipo.value = "";
    filtroEstado.value = "";
    filtroMetodo.value = "";
    filtroDesde.value = "";
    filtroHasta.value = "";

    resetearOrden();

    listaFiltrada = [...listaAnalisis];

    aplicarOrden(); // 🔹 mantener orden actual si existía
    mostrarListado(listaFiltrada);
});

function resetearOrden() {
    encabezados.forEach(th => th.classList.remove("asc", "desc"));
    ordenActual = null;
}


//Analisis Historico
document.getElementById("btnHistorico").addEventListener("click", (e) => {
    e.preventDefault();
    window.location.href = `/site-history?id=${siteId}`;
});

//Volver a la lista de sitios
document.getElementById("btnVolver").addEventListener("click", (e) => {
    e.preventDefault();
    window.location.href = `/site-list`;
});
