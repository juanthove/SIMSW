//Datos ficticios de paginas webs
const listaSitios = [
    {
        id: "1",
        nombre: "Example",
        url: "https://example.com",
        propietario: "Pedro"
    },
    {
        id: "2",
        nombre: "MiDominio",
        url: "https://midominio.com",
        propietario: "Juan"
    },
    {
        id: "3",
        nombre: "TiendaOnline",
        url: "https://tiendaonline.net",
        propietario: "Shop SA"
    }];

const listaFiltrada = [...listaSitios];




const form = document.getElementById("formSitio");
const selector = document.getElementById("selectorSitio");
const btnSubmit = document.getElementById("btnPrincipal");
const tituloForm = document.getElementById("tituloForm");

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

cargarSelectorSitios();


//Cargar datos al seleccionar un sitio, o eliminarlos si se coloca nuevo sitio
selector.addEventListener("change", () => {
  const id = selector.value;

  if (!id) {
    // Nuevo sitio
    sitioSeleccionadoId = null;
    form.reset();
    btnSubmit.textContent = "Registrar sitio";
    tituloForm.textContent = "Registrar sitio web";
    return;
  }

  const sitio = listaFiltrada.find(s => s.id === id);
  if (!sitio) return;

  sitioSeleccionadoId = sitio.id;

  document.getElementById("nombre").value = sitio.nombre;
  document.getElementById("url").value = sitio.url;
  document.getElementById("propietario").value = sitio.propietario;

  btnSubmit.textContent = "Actualizar sitio";
  tituloForm.textContent = "Editar sitio web";
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
      //Al crear un sitio utilizamos POST
      console.log("Creando sitio:", sitio);

      /*
      const res = await fetch("/api/sites", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(sitio)
      });
      */

      alert("Sitio registrado correctamente.");
    } else {
      //Al editar un sitio utilizamos PUT
      console.log("Actualizando sitio:", sitioSeleccionadoId, sitio);

      /*
      const res = await fetch(`/api/sites/${sitioSeleccionadoId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(sitio)
      });
      */

      alert("Sitio actualizado correctamente.");
    }

    form.reset();
    selector.value = "";
    sitioSeleccionadoId = null;
    btnSubmit.textContent = "Registrar sitio";
    tituloForm.textContent = "Registrar sitio web";

  } catch (err) {
    console.error(err);
    alert("Error al conectar con el servidor.");
  }
});