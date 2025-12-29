//Datos ficticios de paginas webs
const listaSitios = [
    {
        id: "1",
        nombre: "Example",
        url: "https://example.com",
        cantAnalisis: "2",
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

mostrarSitios(listaSitios);