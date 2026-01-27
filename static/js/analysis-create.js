//Obtengo datos
let listaSitios = [];
let listaFiltrada = [];


import { apiFetch } from "./api.js";

async function cargarSitios() {
    try {
        const response = await apiFetch("/api/sitios/");

        if (!response.ok) {
            throw new Error("Error al obtener los sitios");
        }

        listaSitios = await response.json();
        listaFiltrada = [...listaSitios];   // ✅ ACÁ
        console.log(listaSitios);
        mostrarListado(listaFiltrada);

    } catch (error) {
        console.error(error);
    }
}

//Cargar los sitios al entrar
cargarSitios()

//Obtengo la tabla
const tablaSitios = document.querySelector("#tablaSitios tbody");

function mostrarListado(lista) {
  tablaSitios.innerHTML = "";

  lista.forEach(item => {
    const tr = document.createElement("tr");

    const estaticoDeshabilitado = !item.archivos_base;

    tr.innerHTML = `
      <td>${item.nombre}</td>
      <td>${item.url}</td>
      <td>
        <button 
          class="btn-estatico ${estaticoDeshabilitado ? "disabled" : ""}"
          data-url="${item.url}"
          data-id="${item.id}"
          ${estaticoDeshabilitado ? "disabled title='Requiere archivos base'" : ""}
        >
          Ejecutar
        </button>
      </td>
      <td>
        <button class="btn-dinamico" data-url="${item.url}" data-id="${item.id}">
          Ejecutar
        </button>
      </td>
    `;

    tablaSitios.appendChild(tr);
  });

  //Crear los event listener para cada boton
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

//Funcion para ejecutar el analisis estatico o dinamico
async function ejecutarAnalisis({ url, sitioWebId, tipo, boton }) {
  boton.disabled = true;
  const textoOriginal = boton.textContent;
  boton.textContent = "⏳ Analizando...";

  const endpoint =
    tipo === "dinamico"
      ? "/analizarDinamico"
      : "/analizarEstatico";

  const token = localStorage.getItem("token");

  try {
    const res = await apiFetch(endpoint, {
      method: "POST",
      body: JSON.stringify({
        url,
        sitio_web_id: sitioWebId
      })
    });

    const data = await res.json();

    if (!res.ok) {
      mostrarToast(data.error || "No autorizado", "error");
      boton.classList.add("error");
      boton.textContent = "❌ Error";
      boton.disabled = false;
      return;
    }

    boton.classList.add("completado");
    boton.textContent = "✔ Completado";
    mostrarToast("Análisis ejecutado correctamente", "success");

  } catch (err) {
    console.error(err);
    boton.classList.add("error");
    boton.textContent = "❌ Error";
    boton.disabled = false;
    mostrarToast("Error al ejecutar el análisis", "error");
  }
}





//Crear los eventListener para cada boton de estatico y dinamico
function enlazarBotonesAnalisis() {
  document.querySelectorAll(".btn-estatico").forEach(btn => {
    btn.addEventListener("click", () => {
      ejecutarAnalisis({
        url: btn.dataset.url,
        sitioWebId: btn.dataset.id,
        tipo: "estatico",
        boton: btn
      });
    });
  });

  document.querySelectorAll(".btn-dinamico").forEach(btn => {
    btn.addEventListener("click", () => {
      ejecutarAnalisis({
        url: btn.dataset.url,
        sitioWebId: btn.dataset.id,
        tipo: "dinamico",
        boton: btn
      });
    });
  });
}

function mostrarToast(mensaje, tipo = "info") {
  const toast = document.getElementById("toast");

  // limpiar clases previas
  toast.className = "toast";

  // setear mensaje y tipo
  toast.textContent = mensaje;
  toast.classList.add(tipo, "show");

  // ocultar luego
  setTimeout(() => {
    toast.classList.remove("show");
  }, 3000);
}
