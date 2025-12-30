//Datos ficticios del sitio para hacer las graficas
const listaAnalisis = [
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
];


const listaFiltrada = [...listaAnalisis];



//Obtener la id del sitio
const params = new URLSearchParams(window.location.search);
const siteId = params.get("id");

if (!siteId) {
    console.error("No se recibió el ID del sitio");
}

const sitio = listaAnalisis.find(s => s.siteId === siteId);
if (!sitio) {
  console.error("Sitio no encontrado");
}

//Valores de cada severidad
const severidades = ["Baja", "Media", "Alta"];
const pesos = {Baja: 1, Media: 2, Alta: 3};

//Colores dependiendo el nivel de severidad
const coloresSeveridad = {
  Baja: "#27ae60",
  Media: "#d68910",
  Alta: "#c0392b"
};


function crearTimelineSeveridad() {
  const fechas = [...new Set(sitio.analisis.map(a => a.fecha))].sort();

  const dataPorSeveridad = {
    Alta: [],
    Media: [],
    Baja: []
  };

  fechas.forEach(fecha => {
    severidades.forEach(sev => {
      const cantidad = sitio.analisis.filter(
        a => a.fecha === fecha && a.vulnerabilidad === sev
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
            precision: 0,
            callback: value => Number.isInteger(value) ? value : null
          }
        }
      }
    }
  });
}

function crearRiesgoAcumulado() {
  const fechas = [...new Set(sitio.analisis.map(a => a.fecha))].sort();

  let acumulado = 0;
  const riesgo = fechas.map(fecha => {
    sitio.analisis
      .filter(a => a.fecha === fecha)
      .forEach(a => acumulado += pesos[a.vulnerabilidad]);
    return acumulado;
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
    }
  });
}

function crearDistribucionSeveridad() {
  const conteo = { Alta: 0, Media: 0, Baja: 0 };

  sitio.analisis.forEach(a => conteo[a.vulnerabilidad]++);

  new Chart(document.getElementById("severityDistributionChart"), {
    type: "pie",
    data: {
      labels: severidades,
      datasets: [{
        data: severidades.map(s => conteo[s]),
        backgroundColor: severidades.map(s => coloresSeveridad[s])
      }]
    }
  });

}

//Insertar las graficas
crearTimelineSeveridad();
crearRiesgoAcumulado();
crearDistribucionSeveridad();

//Volver a analysis-list
document.getElementById("btnVolver").addEventListener("click", (e) => {
    e.preventDefault();
    window.location.href = `analysis-list.html?siteId=${siteId}`;
});
