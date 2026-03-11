//Obtengo datos
import { apiFetch } from "./api.js";
import { formatearFechaDia } from "./fecha.js";


//Obtener la id del sitio
const params = new URLSearchParams(window.location.search);
const siteId = params.get("id");

if (!siteId) {
    console.error("No se recibió el ID del sitio");
}

async function cargarDatos() {
  try {

    //Buscar datos
    const [respInformes, respAlteraciones] = await Promise.all([
      apiFetch(`/api/sitios/${siteId}/informes`),
      apiFetch(`/api/sitios/${siteId}/alteraciones`)
    ]);

    if (!respInformes.ok) {
      throw new Error("Error al obtener informes");
    }

    if (!respAlteraciones.ok) {
      throw new Error("Error al obtener alteraciones");
    }

    const informes = await respInformes.json();
    const alteraciones = await respAlteraciones.json();

    //Formatear fechas sacando la hora
    const informesNormalizados = informes.map(i => ({...i, fechaLocal: formatearFechaDia(i.fecha)}));

    const alteracionesNormalizadas = alteraciones.map(a => ({...a, fechaLocal: formatearFechaDia(a.fecha)}));

    const alteracionesDeduplicadas = deduplicarAlteracionesPorDia(alteracionesNormalizadas);

    //Unir las dos listas
    const todosLosInformes = [...informesNormalizados, ...alteracionesDeduplicadas];

    //Gráficas generales
    crearTimelineSeveridad(todosLosInformes);
    crearRiesgoAcumulado(todosLosInformes);
    crearDistribucionSeveridad(todosLosInformes);

    //Gráfica exclusiva de alteraciones
    crearAlteracionesEnElTiempo(alteracionesDeduplicadas);

  } catch (error) {
    console.error(error);
  }
}


function deduplicarAlteracionesPorDia(alteraciones) {

  const agrupadas = {};

  alteraciones.forEach(a => {
    if (!a.fechaLocal || !a.alteracion_hash) return;

    const fecha = a.fechaLocal;

    if (!agrupadas[fecha]) {
      agrupadas[fecha] = {};
    }

    //Si ese hash no existe todavía en ese día se guarda
    if (!agrupadas[fecha][a.alteracion_hash]) {
      agrupadas[fecha][a.alteracion_hash] = a;
    }
  });

  //Convertimos nuevamente a array plano
  return Object.values(agrupadas)
    .flatMap(hashes => Object.values(hashes));
}

//Colores dependiendo el nivel de severidad
const coloresSeveridad = {
  Baja: "#27ae60",
  Media: "#d68910",
  Alta: "#c0392b",
};

const severidadMap = {
  1: "Baja",
  2: "Media",
  3: "Alta",
};

//Valores de cada severidad
const severidades = ["Baja", "Media", "Alta"];
const pesos = {Baja: 1, Media: 2, Alta: 3};


//Obtener las fechas
function obtenerFechasUnicas(informes) {
  return [...new Set(
    informes.map((i) => i.fechaLocal).filter(Boolean),
  )].sort((a, b) => {
    const [da, ma, ya] = a.split("/");
    const [db, mb, yb] = b.split("/");

    return new Date(ya, ma - 1, da) - new Date(yb, mb - 1, db);
  });
}



function crearTimelineSeveridad(informes) {
  //Fechas únicas
  const fechas = obtenerFechasUnicas(informes);

  const dataPorSeveridad = {
    Alta: [],
    Media: [],
    Baja: [],
  };

  fechas.forEach(fecha => {
    severidades.forEach(sev => {
      const cantidad = informes.filter(i =>
        i.fechaLocal === fecha &&
        severidadMap[i.severidad] === sev
      ).length;

      dataPorSeveridad[sev].push(cantidad);
    });
  });

  new Chart(document.getElementById("severityTimelineChart"), {
    type: "line",
    data: {
      labels: fechas,
      datasets: severidades.map(sev => ({
        label: sev,
        data: dataPorSeveridad[sev],
        borderColor: coloresSeveridad[sev],
        backgroundColor: coloresSeveridad[sev],
        tension: 0.3,
        fill: false
      })),
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            stepSize: 1,
            precision: 0,
          },
        },
      },
    },
  });
}

function crearRiesgoAcumulado(informes) {
  const fechas = obtenerFechasUnicas(informes);

  const riesgo = fechas.map(fecha => {
    return informes
      .filter(i => i.fechaLocal === fecha)
      .reduce((acc, i) => {
        const sevTexto = severidadMap[i.severidad];
        return acc + pesos[sevTexto];
      }, 0);
  });

  new Chart(document.getElementById("riskStackedChart"), {
    type: "bar",
    data: {
      labels: fechas,
      datasets: [{
        label: "Riesgo acumulado",
        data: riesgo,
        backgroundColor: "#34495e",
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
    },
  });
}

function crearDistribucionSeveridad(informes) {
  const conteo = { Alta: 0, Media: 0, Baja: 0 };

  informes.forEach(i => {
    const sev = severidadMap[i.severidad];
    if (sev) conteo[sev]++;
  });

  new Chart(document.getElementById("severityDistributionChart"), {
    type: "pie",
    data: {
      labels: severidades,
      datasets: [{
        data: severidades.map(s => conteo[s]),
        backgroundColor: severidades.map(s => coloresSeveridad[s]),
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
    },
  });
}


function crearAlteracionesEnElTiempo(informes) {

  const conteoPorFecha = {};

  informes.forEach(i => {
    if (!conteoPorFecha[i.fechaLocal]) {
      conteoPorFecha[i.fechaLocal] = 0;
    }
    conteoPorFecha[i.fechaLocal]++;
  });

  const fechas = Object.keys(conteoPorFecha).sort((a, b) => {
    const [da, ma, ya] = a.split("/");
    const [db, mb, yb] = b.split("/");

    return new Date(ya, ma - 1, da) - new Date(yb, mb - 1, db);
  });
  const cantidadPorFecha = fechas.map(f => conteoPorFecha[f]);

  new Chart(document.getElementById("changeTimelineChart"), {
    type: "bar",
    data: {
      labels: fechas,
      datasets: [{
        label: "Cantidad de alteraciones",
        data: cantidadPorFecha,
        backgroundColor: "#8e44ad",
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            stepSize: 1,
            precision: 0,
          },
        },
      },
    },
  });
}



//Volver a analysis-list
document.getElementById("btnVolver").addEventListener("click", (e) => {
    e.preventDefault();
    window.location.href = `/analysis-list?siteId=${siteId}`;
});



//Cargar los sitios al entrar
cargarDatos();