let navBar = document.getElementById("navBarDiv");


if (navBar) {

  navBar.innerHTML = `
    <nav id="navbar">
        <h1>SIMSW</h1>

        <div id="botonEncabezado">
            <div id="analysis">
                <div id="analysis-container">
                    <a href="#" id="analysisBoton">Análisis</a>
                    <div id="analysis-menu">
                        <a href="analysis.html">Realizar Análisis</a>
                        <a href="analysis.html">Ver Análisis</a>
                    </div>
                </div>
                <a href="register.html">Registrar página web</a>
            </div>

            <div id="config">
                <a href="config.html">Configuración</a>
            </div>
        </div>

        <button id="botonMenu">☰</button>
    </nav>`;
}

const botonMenu = document.getElementById("botonMenu");

botonMenu.addEventListener("click", function(){
  document.getElementById("botonEncabezado").classList.toggle('show'); //Activar o desactivar la clase show
});


const analysisContainer = document.getElementById("analysis-container");
const analysisMenu = document.getElementById("analysis-menu");

analysisContainer.addEventListener("mouseenter", () => {
    analysisMenu.classList.add("show");
});

analysisContainer.addEventListener("mouseleave", () => {
    analysisMenu.classList.remove("show");
});