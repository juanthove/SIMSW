//Obtengo datos
let listaSitios = [];
let listaFiltrada = [];


import { apiFetch } from "./api.js";
import { formatearFecha } from "./fecha.js";

async function cargarSitios() {
    try {
        const response = await apiFetch("/api/sitios/resumen");

        if (!response.ok) {
            throw new Error("Error al obtener los sitios");
        }

        listaSitios = await response.json();
        listaFiltrada = [...listaSitios];   // ✅ ACÁ
        console.log(listaSitios);
        mostrarSitios(listaFiltrada);

    } catch (error) {
        console.error(error);
    }
}

//Cargar los sitios al entrar
cargarSitios()




//Obtengo la tabla
const tablaSitios = document.querySelector("#tablaSitios tbody");

function mostrarSitios(lista) {
  tablaSitios.innerHTML = "";

  lista.forEach(item => {
    const tr = document.createElement("tr");

    tr.innerHTML = `
      <td>${item.nombre}</td>
      <td>${item.url}</td>
      <td>${item.cantAnalisis}</td>
      <td>${formatearFecha(item.ultimoAnalisis) ?? "Sin análisis"}</td>
    `;


    if (item.cantAnalisis > 0) {
        tr.style.cursor = "pointer";

        tr.addEventListener("click", () => {
          window.location.href = `/analysis-list?siteId=${item.id}`;
        });
    } else {
        // 👉 Visualmente deshabilitado
        tr.classList.add("site-disabled");
        tr.title = "Este sitio no tiene analisis";
    }
    

    tablaSitios.appendChild(tr);
  });
}

//Filtro ascendente y descendente
const encabezados = document.querySelectorAll("#tablaSitios th.sortable");

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

        if (columna === "vulnerabilidad") {
            A = ordenVulnerabilidad[A];
            B = ordenVulnerabilidad[B];
        }

        if (columna === "titulo") {
          A = A.toLowerCase();
          B = B.toLowerCase();
        }

        if (A < B) return asc ? -1 : 1; //El primer elemento va antes que el segundo
        if (A > B) return asc ? 1 : -1; //El segundo elemento va antes que el primero
        return 0;
    });

    mostrarSitios(listaFiltrada);
  });
});