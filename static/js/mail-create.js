import { apiFetch } from "./api.js";

/* =========================
   VARIABLES GLOBALES
========================= */
let listaSitios = [];
let listaMails = [];

let mailSeleccionadoId = null;

/* =========================
   ELEMENTOS DOM
========================= */
const selectorGmail = document.getElementById("selectorGmail");
const form = document.getElementById("formGmail");
const btnSubmit = document.getElementById("btnPrincipal");
const btnDelete = document.getElementById("btnDelete");
const tituloForm = document.getElementById("tituloForm");

const inputNombre = document.getElementById("nombre");
const inputEmail = document.getElementById("email");

const radioTodos = document.querySelector('input[value="todos"]');
const radioPersonalizado = document.querySelector('input[value="personalizado"]');
const listaSitiosContainer = document.getElementById("listaSitiosContainer");

/* =========================
   CARGA INICIAL
========================= */
cargarSitios();
cargarMails();

/* =========================
   API
========================= */
async function cargarSitios() {
  try {
    const res = await apiFetch("/api/sitios/");
    if (!res.ok) throw new Error("Error al obtener sitios");

    listaSitios = await res.json();
    renderListaSitios();
  } catch (err) {
    console.error(err);
  }
}

async function cargarMails() {
  try {
    const res = await apiFetch("/api/mails/");
    if (!res.ok) throw new Error("Error al obtener gmails");

    listaMails = await res.json();
    cargarSelectorGmail();
  } catch (err) {
    console.error(err);
  }
}

/* =========================
   UI
========================= */
function cargarSelectorGmail() {
  selectorGmail.innerHTML = `<option value="">Nuevo Gmail</option>`;

  listaMails.forEach(mail => {
    const opt = document.createElement("option");
    opt.value = mail.id;
    opt.textContent = `${mail.nombre} — ${mail.email}`;
    selectorGmail.appendChild(opt);
  });
}

function renderListaSitios() {
  listaSitiosContainer.innerHTML = "";

  listaSitios.forEach(sitio => {
    const label = document.createElement("label");
    label.className = "checkboxLabel";

    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.value = sitio.id;

    label.appendChild(checkbox);
    label.append(` ${sitio.nombre}`);

    listaSitiosContainer.appendChild(label);
  });
}

/* =========================
   SELECTOR GMAIL
========================= */
selectorGmail.addEventListener("change", () => {
  const id = selectorGmail.value;

  if (!id) {
    // nuevo
    mailSeleccionadoId = null;
    form.reset();
    btnDelete.style.display = "none";
    btnSubmit.textContent = "Guardar Gmail";
    tituloForm.textContent = "Configurar Gmail";
    listaSitiosContainer.style.display = "none";
    radioTodos.checked = true;
    return;
  }

  const mail = listaMails.find(m => m.id == id);
  if (!mail) return;

  mailSeleccionadoId = mail.id;

  inputNombre.value = mail.nombre;
  inputEmail.value = mail.email;

  btnSubmit.textContent = "Actualizar Gmail";
  tituloForm.textContent = "Editar Gmail";
  btnDelete.style.display = "inline-block";

  // asociaciones
  if (!mail.sitios || mail.sitios.length === 0) {
    radioTodos.checked = true;
    listaSitiosContainer.style.display = "none";
  } else {
    radioPersonalizado.checked = true;
    listaSitiosContainer.style.display = "block";

    document
      .querySelectorAll("#listaSitiosContainer input[type=checkbox]")
      .forEach(cb => {
        cb.checked = mail.sitios.includes(parseInt(cb.value));
      });
  }
});

/* =========================
   RADIOS
========================= */
radioTodos.addEventListener("change", () => {
  listaSitiosContainer.style.display = "none";
});

radioPersonalizado.addEventListener("change", () => {
  listaSitiosContainer.style.display = "block";
});

/* =========================
   SUBMIT
========================= */
form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const nombre = inputNombre.value.trim();
  const email = inputEmail.value.trim();

  if (!nombre || !email) {
    mostrarToast("Todos los campos son obligatorios", "error");
    return;
  }

  const payload = {
    nombre,
    email,
    sitios: null
  };

  if (radioPersonalizado.checked) {
    payload.sitios = Array.from(
      document.querySelectorAll("#listaSitiosContainer input:checked")
    ).map(cb => parseInt(cb.value));
  }

  try {
    let res;

    if (!mailSeleccionadoId) {
      res = await apiFetch("/api/mails/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
    } else {
      res = await apiFetch(`/api/mails/${mailSeleccionadoId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
    }

    const data = await res.json();
    if (!res.ok) throw new Error(data.error);

    mostrarToast(
      mailSeleccionadoId
        ? "Gmail actualizado correctamente"
        : "Gmail creado correctamente",
      "success"
    );

    form.reset();
    selectorGmail.value = "";
    mailSeleccionadoId = null;
    btnDelete.style.display = "none";
    listaSitiosContainer.style.display = "none";

    await cargarMails();

  } catch (err) {
    console.error(err);
    mostrarToast(err.message || "Error al guardar", "error");
  }
});

/* =========================
   ELIMINAR
========================= */
btnDelete.addEventListener("click", async () => {
  if (!mailSeleccionadoId) return;

  const confirmar = await confirmarEliminar();
  if (!confirmar) return;

  try {
    const res = await apiFetch(`/api/mails/${mailSeleccionadoId}`, {
      method: "DELETE"
    });

    if (!res.ok) throw new Error("Error al eliminar");

    mostrarToast("Gmail eliminado correctamente", "success");

    form.reset();
    selectorGmail.value = "";
    mailSeleccionadoId = null;
    btnDelete.style.display = "none";
    listaSitiosContainer.style.display = "none";

    await cargarMails();

  } catch (err) {
    console.error(err);
    mostrarToast("Error al eliminar", "error");
  }
});

/* =========================
   HELPERS
========================= */
function mostrarToast(mensaje, tipo = "info") {
  const toast = document.getElementById("toast");
  toast.className = "toast";
  toast.textContent = mensaje;
  toast.classList.add(tipo, "show");

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
