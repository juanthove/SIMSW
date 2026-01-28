//Obtengo datos
import { apiFetch } from "./api.js";
import { formatearFecha } from "./fecha.js";

//Obtengo el id de la URL
const params = new URLSearchParams(window.location.search);
const siteId = params.get("siteId");

let sitio = null;
let listaAnalisis = [];
let listaFiltrada = [];


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
        console.log(listaAnalisis);
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

const encabezados = document.querySelectorAll("#tablaAnalisis th.sortable");

encabezados.forEach(th => {
  th.addEventListener("click", () => {
    const columna = th.dataset.column;
    const asc = !th.classList.contains("asc");

    // Resetear flechas
    encabezados.forEach(h => h.classList.remove("asc", "desc"));
    th.classList.add(asc ? "asc" : "desc");

    listaFiltrada.sort((a, b) => {
      let A, B;

      switch (columna) {
        case "fecha":
          A = new Date(a.fecha);
          B = new Date(b.fecha);
          break;

        case "resultado":
          A = Number(a.resultado_global);
          B = Number(b.resultado_global);
          break;

        case "vulnerabilidades":
          A = Number(a.cant_vulnerabilidades);
          B = Number(b.cant_vulnerabilidades);
          break;

        case "tipo":
          A = a.tipo?.toLowerCase();
          B = b.tipo?.toLowerCase();
          break;

        case "estado":
          A = a.estado?.toLowerCase();
          B = b.estado?.toLowerCase();
          break;

        default:
          return 0;
      }

      if (A < B) return asc ? -1 : 1;
      if (A > B) return asc ? 1 : -1;
      return 0;
    });

    mostrarListado(listaFiltrada);
  });
});


//Filtros
const filtroTipo = document.getElementById("filtroTipo");
const filtroEstado = document.getElementById("filtroEstado");

function aplicarFiltros() {
  const tipo = filtroTipo.value.toLowerCase().trim();
  const estado = filtroEstado.value.toLowerCase().trim();

  listaFiltrada = listaAnalisis.filter(item => {
    const coincideTipo =
      !tipo || item.tipo?.toLowerCase().trim() === tipo;

    const coincideEstado =
      !estado || item.estado?.toLowerCase().trim() === estado;

    return coincideTipo && coincideEstado;
  });

  mostrarListado(listaFiltrada);
}
// Eventos
filtroTipo.addEventListener("change", aplicarFiltros);
filtroEstado.addEventListener("change", aplicarFiltros);



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
