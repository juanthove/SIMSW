//Lista de analisis provicional
const listaAnalisis = [
  {
    siteId: "1",
    nombre: "Example",
    url: "https://example.com",
    propietario: "Pedro",
    analisis: [
      {
        id: "1",
        titulo: "Exposición de credenciales en código cliente",
        vulnerabilidad: "Alta",
        fecha: "2025-12-10"
      },
      {
        id: "3",
        titulo: "Versiones de librerías desactualizadas",
        vulnerabilidad: "Baja",
        fecha: "2025-12-15"
      }
    ]
  },
  {
    siteId: "2",
    nombre: "MiDominio",
    url: "https://midominio.com",
    propietario: "Juan",
    analisis: [
      {
        id: "2",
        titulo: "Falta de encabezados de seguridad HTTP",
        vulnerabilidad: "Media",
        fecha: "2025-12-12"
      },
      {
        id: "5",
        titulo: "Endpoint expuesto sin autenticación",
        vulnerabilidad: "Alta",
        fecha: "2025-12-18"
      }
    ]
  },
  {
    siteId: "3",
    nombre: "TiendaOnline",
    url: "https://tiendaonline.net",
    propietario: "Shop SA",
    analisis: [
      {
        id: "4",
        titulo: "Configuración de cookies mejorable",
        vulnerabilidad: "Baja",
        fecha: "2025-12-16"
      }
    ]
  }
];

//Obtengo el id de la URL
const params = new URLSearchParams(window.location.search);
const siteId = params.get("siteId");

//Obtengo solo los analisis del sitio seleccionado (CAMBIAR POR FETCH CUANDO TENGAMOS LA API)
const sitioSeleccionado = listaAnalisis.find(
  item => item.siteId === siteId
);

let listaFiltrada = sitioSeleccionado ? sitioSeleccionado.analisis : [];


//Colocar info del sitio
document.getElementById("nombreSitio").textContent = sitioSeleccionado.nombre;
document.getElementById("propietarioSitio").textContent = sitioSeleccionado.propietario;
document.getElementById("urlSitio").textContent = sitioSeleccionado.url;
document.getElementById("cantidadAnalisis").textContent = listaFiltrada.length;


//Orden para mostrar las vulnerabilidades por nivel
const ordenVulnerabilidad = {
  "Baja": 1,
  "Media": 2,
  "Alta": 3,
};

//Obtengo la tabla
const tablaAnalisis = document.querySelector("#tablaAnalisis tbody");

function mostrarListado(lista) {
    tablaAnalisis.innerHTML = ""; //Elimino los datos antiguos

    lista.forEach(item => {
        const tr = document.createElement("tr");

        tr.innerHTML = `
        <td>${item.titulo}</td>
        <td data-vuln="${item.vulnerabilidad}">${item.vulnerabilidad}</td>
        <td>${item.fecha}</td>
        `;

        tr.style.cursor = "pointer";

        tr.addEventListener("click", () => {
            window.location.href = `analysis-detail.html?id=${item.id}`;
        });

        tablaAnalisis.appendChild(tr);
    });
}

const encabezados = document.querySelectorAll("#tablaAnalisis th.sortable");

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

    mostrarListado(listaFiltrada);
  });
});

//Buscador y filtro por nivel
const buscador = document.getElementById("buscadorAnalisis");
const filtroNivel = document.getElementById("filtroNivel");

function aplicarFiltros() {
  const texto = buscador.value.toLowerCase();
  const nivel = filtroNivel.value;

  listaFiltrada = sitioSeleccionado.analisis.filter(item => {
    const coincideTexto =
      item.titulo.toLowerCase().includes(texto);

    const coincideNivel =
      !nivel || item.vulnerabilidad === nivel;

    return coincideTexto && coincideNivel;
  });

  mostrarListado(listaFiltrada);
}

buscador.addEventListener("input", aplicarFiltros);
filtroNivel.addEventListener("change", aplicarFiltros);

//Muestro la tabla al cargar la pagina
mostrarListado(listaFiltrada);