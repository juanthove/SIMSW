//Datos ficticios de paginas webs
const listaSitios = [
    {
        id: "1",
        sitio: "Example",
        url: "https://example.com"
    },
    {
        id: "2",
        sitio: "MiDominio",
        url: "https://midominio.com"
    },
    {
        id: "3",
        sitio: "TiendaOnline",
        url: "https://tiendaonline.net"
    }];

const listaFiltrada = [...listaSitios];

//Obtengo la tabla
const tablaSitios = document.querySelector("#tablaSitios tbody");

function mostrarListado(lista) {
    tablaSitios.innerHTML = ""; //Elimino los datos antiguos

    lista.forEach(item => {
        const tr = document.createElement("tr");

        tr.innerHTML = `
        <td>${item.sitio}</td>
        <td>${item.url}</td>
        <td>
            <button class="btn-estatico" data-url="${item.url}">
            Ejecutar
            </button>
        </td>
        <td>
            <button class="btn-dinamico" data-url="${item.url}">
            Ejecutar
            </button>
        </td>
        `;

        tablaSitios.appendChild(tr);
    });

    //Crear los eventListener para cada boton
    enlazarBotonesAnalisis();
}

//Filtro ascendente y descendente
const encabezados = document.querySelectorAll("#tablaSitios th.sortable");

encabezados.forEach(th => {
  th.addEventListener("click", () => {
    const columna = th.dataset.column;

    //Si no tiene columna, no hacemos nada
    if (!columna) return;

    const asc = !th.classList.contains("asc");

    //Resetear flechas
    encabezados.forEach(h => h.classList.remove("asc", "desc"));

    //Setear la flecha actual
    th.classList.add(asc ? "asc" : "desc");

    listaFiltrada.sort((a, b) => {
      let A = a[columna]?.toLowerCase() ?? "";
      let B = b[columna]?.toLowerCase() ?? "";

      if (A < B) return asc ? -1 : 1;
      if (A > B) return asc ? 1 : -1;
      return 0;
    });

    mostrarListado(listaFiltrada);
  });
});

//Muestro la tabla al iniciar
mostrarListado(listaFiltrada);

//Funcion para ejecutar el analisis estatico o dinamico
async function ejecutarAnalisis({ url, tipo, boton }) {
  boton.disabled = true;
  const textoOriginal = boton.textContent;
  boton.textContent = "⏳ Analizando...";

  const endpoint =
    tipo === "dinamico" ? "/analizarDinamico" : "/analizarEstatico";

  try {
    const res = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url })
    });

    const data = await res.json();

    if (data.error) {
      boton.textContent = "❌ Error";
      boton.disabled = false;
      return;
    }

    boton.textContent = "✔ Completado";

  } catch (err) {
    console.error(err);
    boton.textContent = "❌ Error";
    boton.disabled = false;
  }
}



//Crear los eventListener para cada boton de estatico y dinamico
function enlazarBotonesAnalisis() {
  document.querySelectorAll(".btn-estatico").forEach(btn => {
    btn.addEventListener("click", () => {
      ejecutarAnalisis({
        url: btn.dataset.url,
        tipo: "estatico",
        boton: btn
      });
    });
  });

  document.querySelectorAll(".btn-dinamico").forEach(btn => {
    btn.addEventListener("click", () => {
      ejecutarAnalisis({
        url: btn.dataset.url,
        tipo: "dinamico",
        boton: btn
      });
    });
  });
}
