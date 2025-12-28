//Datos ficticios de paginas webs
const listaSitios = [
    {
        id: "1",
        sitio: "Example",
        url: "https://example.com",
        ultimoAnalisis: "2025-12-15"
    },
    {
        id: "2",
        sitio: "MiDominio",
        url: "https://midominio.com",
        ultimoAnalisis: "2025-12-18"
    },
    {
        id: "3",
        sitio: "TiendaOnline",
        url: "https://tiendaonline.net",
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
      <td>${item.sitio}</td>
      <td>${item.url}</td>
      <td>${item.ultimoAnalisis}</td>
    `;

    tr.style.cursor = "pointer";

    tr.addEventListener("click", () => {
      window.location.href = `analysis-list.html?siteId=${item.id}`;
    });

    tablaSitios.appendChild(tr);
  });
}

mostrarSitios(listaSitios);