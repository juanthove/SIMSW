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
const inputArchivos = document.getElementById("archivosBase");
const archivoInfo = document.getElementById("archivoSeleccionado");
const eliminarArchivosCheckbox = document.getElementById("eliminarArchivos");
const eliminarArchivosContainer = document.getElementById("eliminarArchivosContainer");
const frecuenciaSelect = document.getElementById("frecuenciaSelect");
const customContainer = document.getElementById("frecuenciaCustomContainer");
const customInput = document.getElementById("frecuenciaCustom");
const frecuenciaError = document.getElementById("frecuenciaError");
const fileButton = document.querySelector(".fileButton");

const rutasIgnoradas = ["node_modules", ".git", "venv", "__pycache__"];

function debeIgnorarse(file) {
  const path = file.webkitRelativePath
    .replaceAll("\\", "/")
    .toLowerCase();

  const partes = path.split("/");

  return rutasIgnoradas.some(dir =>
    partes.includes(dir.toLowerCase())
  );
}


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

  //Resetear boton Elegir carpeta
  inputArchivos.disabled = false;
  fileButton.classList.remove("disabled");
  inputArchivos.value = "";
  archivoInfo.textContent = "";

  if (!id) {
    // Nuevo sitio
    sitioSeleccionadoId = null;
    form.reset();
    btnSubmit.textContent = "Registrar sitio";
    tituloForm.textContent = "Registrar sitio web";
    btnDelete.style.display = "none";
    eliminarArchivosContainer.style.display = "none";
    eliminarArchivosCheckbox.checked = false;
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

  if (sitio.archivos_base) {
    eliminarArchivosContainer.style.display = "block";
  } else {
    eliminarArchivosContainer.style.display = "none";
    eliminarArchivosCheckbox.checked = false;
  }
});


frecuenciaSelect.addEventListener("change", () => {
    if (frecuenciaSelect.value === "custom") {
        customContainer.style.display = "block";
        customInput.focus();
    } else {
        customContainer.style.display = "none";
        frecuenciaError.style.display = "none";
    }
});

customInput.addEventListener("input", () => {
    const valor = parseInt(customInput.value, 10);

    if (valor < 15) {
        frecuenciaError.style.display = "block";
    } else {
        frecuenciaError.style.display = "none";
    }
});


form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const nombre = document.getElementById("nombre").value.trim();
  const url = document.getElementById("url").value.trim();
  const propietario = document.getElementById("propietario").value.trim();

  if (!nombre || !url || !propietario) {
    mostrarToast("Todos los campos son obligatorios", "error");
    return;
  }

  let frecuenciaAnalisis;

  if (frecuenciaSelect.value === "custom") {
    frecuenciaAnalisis = parseInt(customInput.value, 10);

    if (!frecuenciaAnalisis || frecuenciaAnalisis < 15) {
      mostrarToast("La frecuencia mínima es de 15 minutos", "error");
      return;
    }
  } else {
    frecuenciaAnalisis = parseInt(frecuenciaSelect.value, 10);
  }

  const formData = new FormData();
  formData.append("nombre", nombre);
  formData.append("url", url);
  formData.append("propietario", propietario);
  formData.append("frecuenciaAnalisis", frecuenciaAnalisis);


  //Eliminar archivos (solo en modificar)
  if (sitioSeleccionadoId && (eliminarArchivosCheckbox.checked || inputArchivos.files.length > 0)) {
    formData.append("eliminarArchivos", "true");
  }

  try {
    let res;

    if (!sitioSeleccionadoId) {
      res = await apiFetch("/api/sitios/", {
        method: "POST",
        body: formData
      });
    } else {
      res = await apiFetch(`/api/sitios/${sitioSeleccionadoId}`, {
        method: "PUT",
        body: formData
      });
    }

    const data = await res.json();

    if (!res.ok) {
      mostrarToast(data.error || "Error al guardar el sitio", "error");
      return;
    }

    //Subir archivos solo si no se marcó eliminar y se seleccionó archivos
    const sitioId = sitioSeleccionadoId ?? data.id;

    let huboArchivoGrande = false;

    if (!eliminarArchivosCheckbox.checked && inputArchivos.files.length > 0) {
      for (const file of inputArchivos.files) {
        if (debeIgnorarse(file)) {
          continue;
        }
        console.log(
          file.name,
          file.webkitRelativePath
        );

        const partes = file.webkitRelativePath.split("/");
        partes.shift(); // elimina la carpeta raíz
        let relativePath = partes.join("/");
        if (!relativePath) {
          relativePath = file.name;
        }

        const fd = new FormData();
        fd.append("archivo", file);
        fd.append("ruta_relativa", relativePath);

        try {
          const resUpload = await apiFetch(
            `/api/sitios/${sitioId}/archivos`,
            {
              method: "POST",
              body: fd
            }
          );

          // 🔴 SOLO archivos demasiado grandes
          if (!resUpload.ok && resUpload.status === 413) {
            huboArchivoGrande = true;

            console.error(
              `Archivo demasiado grande: ${file.name} (${file.size} bytes)`
            );

            mostrarToast(
              `El archivo ${file.name} es demasiado grande`,
              "error"
            );
          }

          // ❌ otros errores (extensión no permitida, ignorados, etc.)
          // no hacen nada y NO muestran mensaje

        } catch (err) {
          // error de red → lo tratamos como archivo grande fallido
          huboArchivoGrande = true;

          console.error(
            `Error de red subiendo ${file.name}:`,
            err
          );

          mostrarToast(
            `Error subiendo ${file.name}`,
            "error"
          );
        }
      }
    }

    // ⚠️ warning SOLO si hubo archivos grandes
    if (huboArchivoGrande) {
      mostrarToast(
        "El sitio se guardó, pero uno o más archivos eran demasiado grandes",
        "warning"
      );
    } else {
      mostrarToast(
        sitioSeleccionadoId
          ? "Sitio actualizado correctamente"
          : "Sitio registrado correctamente",
        "success"
      );
    }


    //Resetear campos
    inputArchivos.disabled = false;
    fileButton.classList.remove("disabled");
    inputArchivos.value = "";
    archivoInfo.textContent = "";

    form.reset();
    selector.value = "";
    sitioSeleccionadoId = null;

    btnSubmit.textContent = "Registrar sitio";
    tituloForm.textContent = "Registrar sitio web";
    btnDelete.style.display = "none";
    eliminarArchivosContainer.style.display = "none";

    frecuenciaSelect.value = "60"; // default 1 hora
    frecuenciaError.style.display = "none";
    customInput.value = "";
    customInput.disabled = false;
    
    
    

    await cargarSitios();

  } catch (err) {
    console.error(err);
    mostrarToast("Error al conectar con el servidor", "error");
  }
});


inputArchivos.addEventListener("change", () => {
  if (inputArchivos.files.length > 0) {
    archivoInfo.textContent = `📁 ${inputArchivos.files.length} archivos seleccionados`;
  } else {
    archivoInfo.textContent = "";
  }
});

// Integración con eliminar archivos
eliminarArchivosCheckbox.addEventListener("change", () => {

  if (eliminarArchivosCheckbox.checked) {
    inputArchivos.value = "";
    inputArchivos.disabled = true;
    fileButton.classList.add("disabled");
    archivoInfo.textContent = "Los archivos actuales serán eliminados";
  } else {
    inputArchivos.disabled = false;
    fileButton.classList.remove("disabled");
    archivoInfo.textContent = "";
  }
});


btnDelete.addEventListener("click", async () => {
  if (!sitioSeleccionadoId) return;

  const confirmar = await confirmarEliminar();
  if (!confirmar) return;

  try {
    const res = await apiFetch(`/api/sitios/${sitioSeleccionadoId}`, {
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
    inputArchivos.disabled = false;
    fileButton.classList.remove("disabled");
    inputArchivos.value = "";
    archivoInfo.textContent = "";
    eliminarArchivosContainer.style.display = "none";

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
