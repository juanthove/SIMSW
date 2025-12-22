const form = document.getElementById("formSitio");

form.addEventListener("submit", async (e) => {
  e.preventDefault(); //Evitar recargar la página

  const nombre = document.getElementById("nombre").value.trim();
  const url = document.getElementById("url").value.trim();
  const propietario = document.getElementById("propietario").value.trim();

  //Validar los campos
  if (!nombre || !url || !propietario) {
    alert("Todos los campos son obligatorios.");
    return;
  }

  const nuevoSitio = {
    nombre,
    url,
    propietario
  };

  console.log("Sitio a registrar:", nuevoSitio);

  try {
    /*CUANDO EXISTA LA API DESCOMENTAR ESTO
       
    const res = await fetch("/api/site", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(nuevoSitio)
    });

    const data = await res.json();

    if (!res.ok) {
      alert(data.error || "Error al registrar el sitio.");
      return;
    }*/

    alert("Sitio registrado correctamente.");

    form.reset();

    // Opcional: redirigir
    // window.location.href = "analysis-create.html";

  } catch (err) {
    console.error("Error:", err);
    alert("Error al conectar con el servidor.");
  }
});