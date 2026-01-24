//Obtengo datos
import { apiFetch } from "./api.js";

//Obtengo el id de la URL
const params = new URLSearchParams(window.location.search);
const siteId = params.get("siteId");
const analysisId = params.get("analysisId");

let listaInformes = [];
let listaFiltrada = [];


async function cargarInformes() {
    try {
        const response = await apiFetch(`/api/analisis/${analysisId}/detalle`);

        if (!response.ok) {
            throw new Error("Error al obtener informes del analisis");
        }

        const data = await response.json();

        document.getElementById("analisis").textContent = data.analisis.tipo;
        document.getElementById("estadoAnalisis").textContent = data.analisis.estado;
        document.getElementById("resultadoGlobal").textContent = data.analisis.resultado_global;
        document.getElementById("fechaAnalisis").textContent = new Date(data.analisis.fecha).toLocaleDateString();

        listaInformes = await data.informes;
        listaFiltrada = [...listaInformes];

        mostrarListado(listaFiltrada);

    } catch (error) {
        console.error(error);
    }
}

//Cargar los sitios al entrar
cargarInformes()


const severidadTexto = {
  1: "Baja",
  2: "Media",
  3: "Alta"
};

//Obtengo la tabla
const tablaInforme = document.querySelector("#tablaInforme tbody");

function mostrarListado(lista) {
    tablaInforme.innerHTML = ""; //Elimino los datos antiguos
    lista.forEach(item => {
        const tr = document.createElement("tr");

        tr.innerHTML = `
        <td>${item.titulo}</td>
        <td>${item.descripcion_humana}</td>
        <td data-vuln="${item.severidad}">${severidadTexto[item.severidad] ?? "Desconocida"}</td>
        `;

        tr.style.cursor = "pointer";

        tr.addEventListener("click", () => {
            window.location.href = `/report-detail?id=${item.id}`;
        });

        tablaInforme.appendChild(tr);
    });
}


const encabezados = document.querySelectorAll("#tablaInforme th.sortable");

encabezados.forEach(th => {
  th.addEventListener("click", () => {
    const columna = th.dataset.column;
    const asc = !th.classList.contains("asc"); //Si no hay una clase asc entonces es que se ordena ascendente

    //Resetear las flechas
    encabezados.forEach(h => h.classList.remove("asc", "desc"));

    //Setear la flecha actual
    th.classList.add(asc ? "asc" : "desc");

    listaFiltrada.sort((a, b) => {
        let A = a[columna];
        let B = b[columna];

        if (columna === "fecha") {
            A = new Date(A);
            B = new Date(B);
        }

        if (columna === "severidad") {
            A = Number(a.severidad);
            B = Number(b.severidad);
        }

        if (columna === "titulo") {
          A = A.toLowerCase();
          B = B.toLowerCase();
        }

        if (A < B) return asc ? -1 : 1; //El primer elemento va antes que el segundo
        if (A > B) return asc ? 1 : -1; //El segundo elemento va antes que el primero
        return 0;
    });

    mostrarListado(listaFiltrada);
  });
});

//Buscador y filtro por nivel
const buscador = document.getElementById("buscadorInforme");
const filtroNivel = document.getElementById("filtroNivel");

function aplicarFiltros() {
  const texto = buscador.value.toLowerCase().trim();
  const nivel = filtroNivel.value; // "Alta" | "Media" | "Baja" | ""

  listaFiltrada = listaInformes.filter(item => {
    const coincideTexto =
      !texto || item.titulo?.toLowerCase().includes(texto);

    const coincideNivel =
      !nivel || severidadTexto[item.severidad] === nivel;

    return coincideTexto && coincideNivel;
  });

  mostrarListado(listaFiltrada);
}




buscador.addEventListener("input", aplicarFiltros);
filtroNivel.addEventListener("change", aplicarFiltros);

//Volver a la lista de sitios
document.getElementById("btnVolver").addEventListener("click", (e) => {
    e.preventDefault();
    window.location.href = `/analysis-list?siteId=${siteId}`;
});

//Muestro la tabla al cargar la pagina
mostrarListado(listaFiltrada);