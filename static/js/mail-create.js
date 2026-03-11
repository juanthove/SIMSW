import { apiFetch } from "./api.js";

let listaSitios = [];
let listaMails = [];

let mailSeleccionadoId = null;


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
const listaCheckbox = document.querySelector("#listaSitiosContainer .listaCheckbox");

//Cargar datos
cargarSitios();
cargarMails();


async function cargarSitios() {
  try {
    const response = await apiFetch("/api/sitios/");
    if (!response.ok) throw new Error("Error al obtener sitios");

    listaSitios = await response.json();
    renderListaSitios();
  } catch (err) {
    console.error(err);
  }
}

async function cargarMails() {
  try {
    const response = await apiFetch("/api/mails/");
    if (!response.ok) throw new Error("Error al obtener gmails");

    listaMails = await response.json();
    cargarSelectorGmail();
  } catch (err) {
    console.error(err);
  }
}


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
  listaCheckbox.innerHTML = "";

  listaSitios.forEach(sitio => {
    const label = document.createElement("label");
    label.className = "checkboxLabel";

    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.value = sitio.id;

    label.appendChild(checkbox);

    const span = document.createElement("span");
    span.classList.add("checkmark");

    label.appendChild(span);
    
    label.append(` ${sitio.nombre}`);

    listaCheckbox.appendChild(label);
  });
}


function displayToast(mensaje, tipo = "info") {
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


selectorGmail.addEventListener("change", () => {
  const id = selectorGmail.value;

  if (!id) {
    //Nuevo
    mailSeleccionadoId = null;
    form.reset();
    btnDelete.style.display = "none";
    btnSubmit.textContent = "Guardar Gmail";
    tituloForm.textContent = "Configurar Gmail";
    listaSitiosContainer.style.display = "none";
    radioTodos.checked = true;
    return;
  }

  const mail = listaMails.find(m => m.id === Number(id));
  if (!mail) {
    return;
  }

  mailSeleccionadoId = mail.id;

  inputNombre.value = mail.nombre;
  inputEmail.value = mail.email;

  btnSubmit.textContent = "Actualizar Gmail";
  tituloForm.textContent = "Editar Gmail";
  btnDelete.style.display = "inline-block";

  //Asociaciones
  if (!mail.sitios || mail.sitios.length === 0) {
    radioTodos.checked = true;
    listaSitiosContainer.style.display = "none";
  } else {
    radioPersonalizado.checked = true;
    listaSitiosContainer.style.display = "block";

    document
      .querySelectorAll("#listaSitiosContainer input[type=checkbox]")
      .forEach(cb => {
        cb.checked = mail.sitios.includes(parseInt(cb.value, 10));
      });
  }
});


radioTodos.addEventListener("change", () => {
  listaSitiosContainer.style.display = "none";
});

radioPersonalizado.addEventListener("change", () => {
  listaSitiosContainer.style.display = "block";
});


form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const nombre = inputNombre.value.trim();
  const email = inputEmail.value.trim();

  if (!nombre || !email) {
    displayToast("Todos los campos son obligatorios", "error");
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
    ).map(cb => parseInt(cb.value, 10));
  }

  try {
    let response;

    if (!mailSeleccionadoId) {
      response = await apiFetch("/api/mails/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
    } else {
      response = await apiFetch(`/api/mails/${mailSeleccionadoId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
    }

    const data = await response.json();
    if (!response.ok) throw new Error(data.error);

    displayToast(
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
    displayToast(err.message || "Error al guardar", "error");
  }
});


btnDelete.addEventListener("click", async () => {
  if (!mailSeleccionadoId) return;

  const confirmar = await confirmarEliminar();
  if (!confirmar) return;

  try {
    const response = await apiFetch(`/api/mails/${mailSeleccionadoId}`, {
      method: "DELETE"
    });

    if (!response.ok) throw new Error("Error al eliminar");

    displayToast("Gmail eliminado correctamente", "success");

    form.reset();
    selectorGmail.value = "";
    mailSeleccionadoId = null;
    btnDelete.style.display = "none";
    listaSitiosContainer.style.display = "none";

    await cargarMails();

  } catch (err) {
    console.error(err);
    displayToast("Error al eliminar", "error");
  }
});

