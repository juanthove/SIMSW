//Listado de detalles provicional
const listaAnalisisDetalle = [
  {
    id: "1",
    siteId: "1",
    sitio: "Example",
    url: "https://example.com",
    vulnerabilidad: "Alta",
    fecha: "2025-12-10",
    titulo: "Exposición de credenciales en código cliente",
    descripcion: "Se detectaron claves de acceso embebidas en archivos JavaScript públicos, accesibles desde el navegador sin autenticación.",
    impacto: "Un atacante podría reutilizar las credenciales para acceder a servicios internos, comprometiendo datos sensibles.",
    recomendacion: "Eliminar las credenciales del código cliente y utilizar variables de entorno en el servidor.",
    evidencia: "Archivo app.js línea 142 contiene una API key visible.",
    severidadNumerica: 3,
    fuenteAnalisis: "Análisis estático",
    fechaAnalisis: "2025-12-10T14:32:00",
    codigo: `
            if not url:
                return jsonify({"error": "No se proporcionó URL"}), 400
            `
  },
  {
    id: "2",
    siteId: "2",
    sitio: "MiDominio",
    url: "https://midominio.com",
    vulnerabilidad: "Media",
    fecha: "2025-12-12",
    titulo: "Falta de encabezados de seguridad HTTP",
    descripcion: "El sitio no implementa encabezados HTTP como Content-Security-Policy y X-Frame-Options.",
    impacto: "Podría facilitar ataques de clickjacking o ejecución de scripts no autorizados.",
    recomendacion: "Configurar encabezados de seguridad a nivel del servidor web.",
    evidencia: "Respuesta HTTP carece de CSP y X-Frame-Options.",
    severidadNumerica: 2,
    fuenteAnalisis: "Análisis estático",
    fechaAnalisis: "2025-12-12T09:18:00"
  },
  {
    id: "3",
    siteId: "1",
    sitio: "Example",
    url: "https://example.com",
    vulnerabilidad: "Baja",
    fecha: "2025-12-15",
    titulo: "Versiones de librerías desactualizadas",
    descripcion: "Se identificaron librerías JavaScript con versiones antiguas sin parches recientes.",
    impacto: "Riesgo bajo, aunque podría facilitar exploits conocidos en el futuro.",
    recomendacion: "Actualizar las dependencias a versiones mantenidas.",
    evidencia: "jQuery 2.1.4 detectado en vendor.js.",
    severidadNumerica: 1,
    fuenteAnalisis: "Análisis dinámico",
    fechaAnalisis: "2025-12-15T11:47:00"
  },
  {
    id: "4",
    siteId: "3",
    sitio: "TiendaOnline",
    url: "https://tiendaonline.net",
    vulnerabilidad: "Baja",
    fecha: "2025-12-16",
    titulo: "Configuración de cookies mejorable",
    descripcion: "Las cookies de sesión no incluyen el flag SameSite.",
    impacto: "Posible exposición a ataques CSRF en escenarios específicos.",
    recomendacion: "Configurar cookies con SameSite=Strict o Lax según el caso.",
    evidencia: "Cookie PHPSESSID sin atributo SameSite.",
    severidadNumerica: 1,
    fuenteAnalisis: "Análisis estático",
    fechaAnalisis: "2025-12-16T16:05:00"
  },
  {
    id: "5",
    siteId: "2",
    sitio: "MiDominio",
    url: "https://midominio.com",
    vulnerabilidad: "Alta",
    fecha: "2025-12-18",
    titulo: "Endpoint expuesto sin autenticación",
    descripcion: "Se detectó un endpoint de administración accesible sin credenciales.",
    impacto: "Permite a un atacante modificar información crítica del sistema.",
    recomendacion: "Restringir el acceso mediante autenticación y controles de rol.",
    evidencia: "GET /admin/config responde HTTP 200 sin token.",
    severidadNumerica: 3,
    fuenteAnalisis: "Análisis dinámico",
    fechaAnalisis: "2025-12-18T10:22:00"
  },
  {
    id: "6",
    siteId: "1",
    sitio: "Example",
    url: "https://example.com",
    vulnerabilidad: "Alta",
    fecha: "2025-12-20",
    titulo: "Endpoint crítico expuesto sin autenticación",
    descripcion: "Se identificó un endpoint sensible accesible sin ningún mecanismo de autenticación, permitiendo ejecutar operaciones administrativas desde el navegador.",
    impacto: "Un atacante podría acceder, modificar o eliminar información crítica del sistema, comprometiendo completamente la integridad del sitio.",
    recomendacion: "Implementar autenticación y autorización robusta en el endpoint, restringiendo el acceso por roles y validando sesiones.",
    evidencia: "Petición GET a /api/admin/config devuelve información sensible sin token de acceso.",
    severidadNumerica: 3,
    fuenteAnalisis: "Análisis dinámico",
    fechaAnalisis: "2025-12-20T16:45:00",
    codigo: `
      @app.route('/api/admin/config')
      def admin_config():
          return jsonify(config)
    `
  },
  {
    id: "7",
    siteId: "1",
    sitio: "Example",
    url: "https://example.com",
    vulnerabilidad: "Media",
    fecha: "2025-12-22",
    titulo: "Falta de encabezados de seguridad HTTP",
    descripcion: "La aplicación no envía encabezados de seguridad recomendados, como Content-Security-Policy y X-Frame-Options, exponiendo el sitio a ataques del lado del cliente.",
    impacto: "Podría facilitar ataques como clickjacking o la ejecución de scripts maliciosos en el navegador del usuario.",
    recomendacion: "Configurar encabezados de seguridad HTTP adecuados en el servidor web o framework backend.",
    evidencia: "Respuesta HTTP sin los encabezados CSP, X-Frame-Options y X-Content-Type-Options.",
    severidadNumerica: 2,
    fuenteAnalisis: "Análisis automático",
    fechaAnalisis: "2025-12-22T11:10:00",
    codigo: `
      response = make_response(render_template("index.html"))
      return response
    `
  }
];


const params = new URLSearchParams(window.location.search);
const id = params.get("id");
//Agarro el el analisis especifico
const analisis = listaAnalisisDetalle.find(a => a.id === id);

/*fetch(`https://tu-api.com/analisis/${id}`) Realizo el fetch (completar cuando se haga la base de datos)
  .then(res => res.json())
  .then(data => mostrarDetalle(data))
  .catch(err => console.error(err));*/

function mostrarDetalle(data) {
    document.getElementById("titulo").textContent = data.titulo;
    document.getElementById("nivel").textContent = data.vulnerabilidad;
    document.getElementById("nivel").classList.add(data.vulnerabilidad);

    document.getElementById("sitio").textContent = data.sitio;
    document.getElementById("url").textContent = data.url;
    document.getElementById("url").href = data.url;
    document.getElementById("fecha").textContent = data.fecha;
    document.getElementById("fuente").textContent = data.fuenteAnalisis;

    document.getElementById("descripcion").textContent = data.descripcion;
    document.getElementById("impacto").textContent = data.impacto;
    document.getElementById("recomendacion").textContent = data.recomendacion;
    document.getElementById("evidencia").textContent = data.evidencia;

    if (data.codigo) {
        document.getElementById("codigo").textContent = data.codigo;
        document.getElementById("bloqueCodigo").hidden = false;
    }
}

//Volver a la lista de analisis
document.getElementById("btnVolver").addEventListener("click", (e) => {
    e.preventDefault();
    window.location.href = `analysis-list.html?siteId=${analisis.siteId}`;
});

mostrarDetalle(analisis);