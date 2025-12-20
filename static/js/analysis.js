//Lista de analisis provicional
const listaAnalisis = [
    {
        id: "1",
        sitio: "https://example.com",
        vulnerabilidad: "Alta",
        fecha: "2025-12-10"
    },
    {
        id: "2",
        sitio: "https://midominio.com",
        vulnerabilidad: "Media",
        fecha: "2025-12-12"
    },
    {
        id: "3",
        sitio: "https://example.com",
        vulnerabilidad: "Baja",
        fecha: "2025-12-15"
    },
    {
        id: "4",
        sitio: "https://tiendaonline.net",
        vulnerabilidad: "Baja",
        fecha: "2025-12-16"
    },
    {
        id: "5",
        sitio: "https://midominio.com",
        vulnerabilidad: "Alta",
        fecha: "2025-12-18"
    }];


let listaFiltrada = listaAnalisis;

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
        <td>${item.sitio}</td>
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

        if (A < B) return asc ? -1 : 1; //El primer elemento va antes que el segundo
        if (A > B) return asc ? 1 : -1; //El segundo elemento va antes que el primero
        return 0;
    });

    mostrarListado(listaFiltrada);
  });
});

//Buscador
const buscador = document.getElementById("buscadorAnalisis");

buscador.addEventListener("input", () => {
  const texto = buscador.value.toLowerCase();

  listaFiltrada = listaAnalisis.filter(item =>
    item.sitio.toLowerCase().includes(texto)
  );

  mostrarListado(listaFiltrada);
});

//Muestro la tabla al cargar la pagina
mostrarListado(listaFiltrada);