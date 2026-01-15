//Obtengo datos
let listaSitios = [];
let listaFiltrada = [];

async function cargarSitios() {
    try {
        const response = await fetch("/api/sitios/", {
            method: "GET",
            headers: {
                "Content-Type": "application/json"
            }
        });

        if (!response.ok) {
            throw new Error("Error al obtener los sitios");
        }

        listaSitios = await response.json();
        listaFiltrada = [...listaSitios];   // ✅ ACÁ
        console.log(listaSitios);

        cargarSelectorSitios();             // ✅ ACÁ

    } catch (error) {
        console.error(error);
    }
}


cargarSitios();


const form = document.getElementById("formSitio");
const selector = document.getElementById("selectorSitio");
const btnSubmit = document.getElementById("btnPrincipal");
const tituloForm = document.getElementById("tituloForm");
const btnDelete = document.getElementById("btnDelete");

let sitioSeleccionadoId = null;

//Cargar los sitios registrados en el selector
function cargarSelectorSitios() {
  selector.innerHTML = `<option value="">Nuevo sitio</option>`;

  listaFiltrada.forEach(sitio => {
    const option = document.createElement("option");
    option.value = sitio.id;
    option.textContent = `${sitio.nombre} — ${sitio.url}`;
    selector.appendChild(option);
  });
}


//Cargar datos al seleccionar un sitio, o eliminarlos si se coloca nuevo sitio
selector.addEventListener("change", () => {
  const id = selector.value;

  if (!id) {
    // Nuevo sitio
    sitioSeleccionadoId = null;
    form.reset();
    btnSubmit.textContent = "Registrar sitio";
    tituloForm.textContent = "Registrar sitio web";
    btnDelete.style.display = "none";
    return;
  }

  const sitio = listaFiltrada.find(s => s.id == id);
  if (!sitio) return;

  sitioSeleccionadoId = sitio.id;

  document.getElementById("nombre").value = sitio.nombre;
  document.getElementById("url").value = sitio.url;
  document.getElementById("propietario").value = sitio.propietario;

  btnSubmit.textContent = "Actualizar sitio";
  tituloForm.textContent = "Editar sitio web";
  btnDelete.style.display = "inline-block";
});



form.addEventListener("submit", async (e) => {
  e.preventDefault(); //Evitar que la pagina se recargue

  const nombre = document.getElementById("nombre").value.trim();
  const url = document.getElementById("url").value.trim();
  const propietario = document.getElementById("propietario").value.trim();

  if (!nombre || !url || !propietario) {
    alert("Todos los campos son obligatorios.");
    return;
  }

  const sitio = { nombre, url, propietario };

  try {
    if (!sitioSeleccionadoId) {
      // Crear sitio (POST)
      console.log("Creando sitio:", sitio);

      const res = await fetch("/api/sitios", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(sitio)
      });

      const data = await res.json();

      if (!res.ok) {
        mostrarToast(data.error || "Error al registrar el sitio", "error");
        return;
      }

      mostrarToast("Sitio registrado correctamente", "success");
      cargarSitios(); // GET nuevamente
      form.reset();

    } else {
      // Editar sitio (PUT) – todavía no implementado
      console.log("Actualizando sitio:", sitioSeleccionadoId, sitio);

      
      const res = await fetch(`/api/sitios/${sitioSeleccionadoId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(sitio)
      });

      const data = await res.json();

      if (!res.ok) {
        mostrarToast(data.error || "Error al actualizar sitio", "error");
        return;
      }

      mostrarToast("Sitio actualizado correctamente", "success");
      cargarSitios(); // GET nuevamente
      form.reset();
    }

    // Reset UI (común a POST y PUT)
    form.reset();
    selector.value = "";
    sitioSeleccionadoId = null;
    btnSubmit.textContent = "Registrar sitio";
    tituloForm.textContent = "Registrar sitio web";

  } catch (err) {
    console.error(err);
    alert(err.message || "Error al conectar con el servidor.");
  }

});

btnDelete.addEventListener("click", async () => {
  if (!sitioSeleccionadoId) return;

  const confirmar = await confirmarEliminar();
  if (!confirmar) return;

  try {
    const res = await fetch(`/api/sitios/${sitioSeleccionadoId}`, {
      method: "DELETE"
    });

    if (!res.ok) {
      const error = await res.json();
      throw new Error(error.error || "Error al eliminar el sitio");
    }

    mostrarToast("Sitio eliminado correctamente", "success");

    // Reset UI
    form.reset();
    selector.value = "";
    sitioSeleccionadoId = null;
    btnSubmit.textContent = "Registrar sitio";
    tituloForm.textContent = "Registrar sitio web";
    btnDelete.style.display = "none";

    // Recargar lista
    await cargarSitios();

  } catch (err) {
    console.error(err);
    alert(err.message || "Error al eliminar el sitio");
  }
});

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





function confirmarEliminar() {
  return new Promise((resolve) => {
    const modal = document.getElementById("confirmModal");
    const btnOk = document.getElementById("btnConfirmar");
    const btnCancel = document.getElementById("btnCancelar");

    modal.classList.remove("hidden");

    btnOk.onclick = () => {
      modal.classList.add("hidden");
      resolve(true);
    };

    btnCancel.onclick = () => {
      modal.classList.add("hidden");
      resolve(false);
    };
  });
}
