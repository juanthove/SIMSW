//Obtengo datos
import { apiFetch } from "./api.js";


//Obtener la id del sitio
const params = new URLSearchParams(window.location.search);
const siteId = params.get("id");

if (!siteId) {
    console.error("No se recibió el ID del sitio");
}

async function cargarDetalle() {
    try {
        const response = await apiFetch(`/api/sitios/${siteId}/informes`);

        if (!response.ok) {
            throw new Error("Error al obtener informes del analisis");
        }

        const historico = await response.json();

        //Insertar las graficas
        crearTimelineSeveridad(historico);
        crearRiesgoAcumulado(historico);
        crearDistribucionSeveridad(historico);

    } catch (error) {
        console.error(error);
    }
}

//Cargar los sitios al entrar
cargarDetalle()

//Colores dependiendo el nivel de severidad
const coloresSeveridad = {
  Baja: "#27ae60",
  Media: "#d68910",
  Alta: "#c0392b"
};

const severidadMap = {
  1: "Baja",
  2: "Media",
  3: "Alta"
};

//Valores de cada severidad
const severidades = ["Baja", "Media", "Alta"];
const pesos = {Baja: 1, Media: 2, Alta: 3};


function crearTimelineSeveridad(informes) {
  // Fechas únicas
  const fechas = [...new Set(
    informes.map(i => i.fecha?.split("T")[0])
  )].sort();

  const dataPorSeveridad = {
    Alta: [],
    Media: [],
    Baja: []
  };

  fechas.forEach(fecha => {
    severidades.forEach(sev => {
      const cantidad = informes.filter(i =>
        i.fecha?.startsWith(fecha) &&
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
      }))
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            stepSize: 1,
            precision: 0
          }
        }
      }
    }
  });
}

function crearRiesgoAcumulado(informes) {
  const fechas = [...new Set(
    informes.map(i => i.fecha?.split("T")[0])
  )].sort();

  const riesgo = fechas.map(fecha => {
    return informes
      .filter(i => i.fecha?.startsWith(fecha))
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
        backgroundColor: "#34495e"
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false
    }
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
        backgroundColor: severidades.map(s => coloresSeveridad[s])
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false
    }
  });
}

//Volver a analysis-list
document.getElementById("btnVolver").addEventListener("click", (e) => {
    e.preventDefault();
    window.location.href = `/analysis-list?siteId=${siteId}`;
});








/*const listaAnalisis = [
  {
    siteId: "1",
    nombre: "Example",
    url: "https://example.com",
    propietario: "Pedro",
    analisis: [
      {
        id: "1",
        titulo: "Exposición de credenciales en código cliente",
        vulnerabilidad: "Alta",
        fecha: "2025-12-10"
      },
      {
        id: "3",
        titulo: "Versiones de librerías desactualizadas",
        vulnerabilidad: "Baja",
        fecha: "2025-12-15"
      },
      {
        id: "6",
        titulo: "Endpoint crítico expuesto sin autenticación",
        vulnerabilidad: "Alta",
        fecha: "2025-12-20"
      },
      {
        id: "7",
        titulo: "Falta de encabezados de seguridad HTTP",
        vulnerabilidad: "Media",
        fecha: "2025-12-22"
      },
      {
        id: "8",
        titulo: "Exposición de credenciales en código cliente",
        vulnerabilidad: "Alta",
        fecha: "2025-12-10"
      },
      {
        id: "9",
        titulo: "Exposición de credenciales en código cliente",
        vulnerabilidad: "Media",
        fecha: "2025-12-10"
      },
      {
        id: "10",
        titulo: "Exposición de credenciales en código cliente",
        vulnerabilidad: "Media",
        fecha: "2025-12-15"
      }
    ]
  },
  {
    siteId: "2",
    nombre: "MiDominio",
    url: "https://midominio.com",
    propietario: "Juan",
    analisis: [
      {
        id: "2",
        titulo: "Falta de encabezados de seguridad HTTP",
        vulnerabilidad: "Media",
        fecha: "2025-12-12"
      },
      {
        id: "5",
        titulo: "Endpoint expuesto sin autenticación",
        vulnerabilidad: "Alta",
        fecha: "2025-12-18"
      }
    ]
  },
  {
    siteId: "3",
    nombre: "TiendaOnline",
    url: "https://tiendaonline.net",
    propietario: "Shop SA",
    analisis: [
      {
        id: "4",
        titulo: "Configuración de cookies mejorable",
        vulnerabilidad: "Baja",
        fecha: "2025-12-16"
      }
    ]
  }
];*/


/*const listaFiltrada = [...listaAnalisis];





const sitio = listaAnalisis.find(s => s.siteId === siteId);
if (!sitio) {
  console.error("Sitio no encontrado");
}

//Valores de cada severidad
const severidades = ["Baja", "Media", "Alta"];
const pesos = {Baja: 1, Media: 2, Alta: 3};*/


