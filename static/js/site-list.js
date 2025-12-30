//Datos ficticios de paginas webs
const listaSitios = [
    {
        id: "1",
        nombre: "Example",
        url: "https://example.com",
        cantAnalisis: "4",
        ultimoAnalisis: "2025-12-15"
    },
    {
        id: "2",
        nombre: "MiDominio",
        url: "https://midominio.com",
        cantAnalisis: "2",
        ultimoAnalisis: "2025-12-18"
    },
    {
        id: "3",
        nombre: "TiendaOnline",
        url: "https://tiendaonline.net",
        cantAnalisis: "1",
        ultimoAnalisis: "2025-12-16"
    }];

const listaFiltrada = [...listaSitios];

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
      <td>${item.ultimoAnalisis}</td>
    `;

    tr.style.cursor = "pointer";

    tr.addEventListener("click", () => {
      window.location.href = `analysis-list.html?siteId=${item.id}`;
    });

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

mostrarSitios(listaSitios);