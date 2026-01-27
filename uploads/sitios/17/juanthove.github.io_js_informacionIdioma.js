let idiomaActual = "en";

let modoOscuro = true;

let proyectos = [];
let tecnologias = [];

const botonEspañol = document.getElementById("botonEsp");
const botonIngles = document.getElementById("botonEng");

//Funcion que cambia el modo
function getModoTexto(){
  return modoOscuro ? "Blanco" : "Negro";
}



//Inserto los proyectos en el HTML
function mostrarProyectos(proyectos){

  let contenedorProyectos = document.getElementById("proyectosLista");
  contenedorProyectos.replaceChildren();

  //Inserto los datos principales del proyecto
  proyectos.forEach(item => {
    //Creo el div que contiene la imagen y los textos
    let divGeneral = document.createElement("div");
    divGeneral.classList.add("proyecto");

    //Creo el carrusel con las imagenes
    let carrusel = document.createElement("div");
    carrusel.classList.add("carrusel");

    //Creo el contenedor de las imagenes
    let contenedorImagenes = document.createElement("div");
    contenedorImagenes.classList.add("imagenesCarrusel");

    //Inserto todas las imagenes
    item.image.forEach((imgSrc, index) => {
      let imagen = document.createElement("img");
      imagen.src = imgSrc;
      imagen.alt = item.title;
      imagen.classList.add("imagenProyecto");
      if (index !== 0){
        imagen.style.display = "none"; //Oculta todas las imagenes que no sean la primera
      }
      contenedorImagenes.appendChild(imagen);
    });

    //Creo el contenedor para los puntos
    let contenedorPuntos = document.createElement("div");
    contenedorPuntos.classList.add("contenedorPuntos");

    //Inserto todos los puntos que representa cada imagen
    item.image.forEach((_, index) => {
      let punto = document.createElement("div");
      punto.classList.add("puntoImagen");
      if (index === 0){
        punto.classList.add("puntoActivo") //Activa el primer punto que representa la primer imagen
      }
      contenedorPuntos.appendChild(punto);
    });
    

    //Creo los botones de antes y despues
    let botonAnt = document.createElement("button");
    botonAnt.classList.add("botonImgProyectoAnt");

    let botonSig = document.createElement("button");
    botonSig.classList.add("botonImgProyectoSig");

    //Creo el svg para las imagenes de los botones
    let svgAnt = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svgAnt.setAttribute("viewBox", "0 0 920 920");
    svgAnt.classList.add("svgFlechas");
    
    let pathAnt = document.createElementNS("http://www.w3.org/2000/svg", "path");
    pathAnt.setAttribute("d", "m 477.56682,624.37003 c 6.05,-0.76392 14.375,-1.80792 18.5,-2.32 11.3815,-1.4129 30.16879,-5.46263 39.5,-8.51449 2.19999,-0.71954 6.69999,-2.08046 10,-3.02428 3.3,-0.94382 7.35,-2.27844 9,-2.96584 1.64999,-0.68739 7.49717,-3.00382 12.99374,-5.14761 8.70028,-3.39333 23.49937,-10.51264 38.47776,-18.51027 7.67925,-4.10029 28.08498,-18.07531 38.5285,-26.38653 12.33705,-9.81815 40.16962,-37.72094 50.37395,-50.50101 7.69161,-9.63313 22.95796,-31.78149 25.97565,-37.6854 14.98969,-29.32622 22.55656,-46.58262 26.667,-60.8146 0.95309,-3.3 2.1095,-6.9 2.56978,-8 2.32224,-5.54975 7.81527,-31.9514 9.36254,-45 0.26087,-2.2 1.16207,-9.625 2.0027,-16.5 1.94877,-15.93806 1.94877,-36.06194 0,-52 -0.84063,-6.875 -1.74183,-14.3 -2.0027,-16.5 -1.58554,-13.3713 -7.15177,-39.94617 -9.42546,-45 -0.49487,-1.1 -1.64454,-4.7 -2.5548,-8 -3.6094,-13.08523 -14.5267,-37.91891 -26.82682,-61.02318 -3.95003,-7.41964 -18.02936,-27.88238 -26.0385,-37.84407 C 684.3835,105.83829 657.25909,78.706209 644.53944,68.487851 635.14874,60.943803 611.80308,44.873142 605.86769,41.867032 576.69182,27.090263 558.97745,19.3429 545.56682,15.494502 c -3.30001,-0.946988 -7.80001,-2.310505 -10,-3.030037 -6.38899,-2.089581 -24.37966,-6.2254158 -32,-7.3564078 -28.56646,-4.23975795 -37.52419,-5.09197483 -53.5,-5.08986286 -7.42501,9.8157e-4 -19.125,0.6895636 -26,1.53018226 -6.875,0.8406187 -14.30001,1.7418364 -16.5,2.0027059 -14.92021,1.7691949 -35.85372,6.3471503 -51,11.1532085 -18.32755,5.815504 -39.25128,14.996519 -63.02319,27.653611 -7.37783,3.928249 -27.85859,18.010481 -37.69177,25.916247 -12.17994,9.792524 -42.38728,39.861361 -50.56715,50.335281 -7.04569,9.02167 -22.67871,31.93578 -25.84934,37.88873 -7.88846,14.81072 -18.18387,36.21655 -18.75846,39.00184 -0.11344,0.55 -0.69002,1.9 -1.28125,3 -0.59123,1.1 -3.13368,8.075 -5.64989,15.5 -6.37063,18.79884 -11.04066,38.89779 -13.12788,56.5 -0.26086,2.2 -1.16207,9.625 -2.0027,16.5 -0.84061,6.875 -1.5284,18.575 -1.5284,26 0,7.425 0.68778,19.125 1.5284,26 0.84062,6.875 1.74184,14.3 2.0027,16.5 1.77161,14.94056 6.3582,35.90351 11.15856,51 11.50379,36.17788 30.39279,71.66285 53.76332,101 9.60072,12.05183 39.15288,41.69975 50.12109,50.2835 8.39771,6.57207 29.89941,21.24373 37.40595,25.52392 6.59963,3.76307 29.39033,15.01323 37.64935,18.58483 16.83076,7.27842 50.42453,16.86468 66.85065,19.07638 4.4,0.59244 10.7,1.51105 14,2.04136 20.26454,3.25648 46.67125,3.80064 66.00001,1.36004 z m 15.98852,-157.23631 c -5.69935,-2.58913 -143.00891,-139.86753 -145.59546,-145.56241 -2.30822,-5.08207 -2.41076,-12.67811 -0.23307,-17.26722 2.52184,-5.3144 140.59559,-143.06181 145.74479,-145.40032 17.81577,-8.09106 35.87454,10.99046 26.92624,28.4512 -0.88647,1.72977 -28.88609,30.46544 -62.2214,63.85705 -33.3353,33.39161 -60.60962,61.19681 -60.60962,61.78933 0,0.59253 27.27884,28.39712 60.61964,61.78799 33.3408,33.39086 61.34042,62.12592 62.2214,63.85569 8.8847,17.44501 -9.11837,36.54506 -26.85252,28.48869 z");
    pathAnt.setAttribute("fill", "currentColor");

    //Coloco el path dentro del svg y el svg dentro del boton
    svgAnt.appendChild(pathAnt);
    botonAnt.appendChild(svgAnt);

    let svgSig = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svgSig.setAttribute("viewBox", "0 0 920 920");
    svgSig.classList.add("svgFlechas");

    let pathSig = document.createElementNS("http://www.w3.org/2000/svg", "path");
    pathSig.setAttribute("d", "m 422.5,624.37003 c -6.05,-0.76392 -14.375,-1.80792 -18.5,-2.32 -11.38151,-1.4129 -30.16879,-5.46263 -39.5,-8.51449 -2.2,-0.71954 -6.7,-2.08046 -10,-3.02428 -3.3,-0.94382 -7.35,-2.27844 -9,-2.96584 -1.65,-0.68739 -7.49718,-3.00382 -12.99374,-5.14761 -8.70028,-3.39333 -23.49938,-10.51264 -38.47777,-18.51027 C 286.34925,579.78725 265.94352,565.81223 255.5,557.50101 243.16294,547.68286 215.33037,519.78007 205.12605,507 197.43443,497.36687 182.16808,475.21851 179.15039,469.3146 164.1607,439.98838 156.59383,422.73198 152.4834,408.5 c -0.9531,-3.3 -2.1095,-6.9 -2.56978,-8 -2.32224,-5.54975 -7.81527,-31.9514 -9.36254,-45 -0.26087,-2.2 -1.16208,-9.625 -2.0027,-16.5 -1.94878,-15.93806 -1.94878,-36.06194 0,-52 0.84062,-6.875 1.74183,-14.3 2.0027,-16.5 1.58553,-13.3713 7.15176,-39.94617 9.42545,-45 0.49488,-1.1 1.64455,-4.7 2.55481,-8 3.6094,-13.08523 14.5267,-37.91891 26.82682,-61.02318 3.95003,-7.41964 18.02935,-27.88238 26.03849,-37.84407 10.28667,-12.79446 37.41108,-39.926541 50.13072,-50.144899 9.3907,-7.544048 32.73637,-23.614709 38.67176,-26.620819 C 323.37499,27.090263 341.08936,19.3429 354.5,15.494502 c 3.3,-0.946988 7.8,-2.310505 10,-3.030037 6.38898,-2.089581 24.37965,-6.2254158 32,-7.3564078 28.56646,-4.23975795 37.52419,-5.09197483 53.5,-5.08986286 7.425,9.8157e-4 19.125,0.6895636 26,1.53018226 6.875,0.8406187 14.3,1.7418364 16.5,2.0027059 14.92021,1.7691949 35.85372,6.3471503 51,11.1532085 18.32755,5.815504 39.25128,14.996519 63.02318,27.653611 7.37783,3.928249 27.85859,18.010481 37.69177,25.916247 12.17994,9.792524 42.38728,39.861361 50.56715,50.335281 7.04569,9.02167 22.67871,31.93578 25.84935,37.88873 7.88846,14.81072 18.18387,36.21655 18.75845,39.00184 0.11345,0.55 0.69002,1.9 1.28125,3 0.59123,1.1 3.13368,8.075 5.64989,15.5 6.37063,18.79884 11.04066,38.89779 13.12788,56.5 0.26087,2.2 1.16208,9.625 2.0027,16.5 0.84062,6.875 1.5284,18.575 1.5284,26 0,7.425 -0.68778,19.125 -1.5284,26 -0.84062,6.875 -1.74183,14.3 -2.0027,16.5 -1.77161,14.94056 -6.3582,35.90351 -11.15856,51 -11.50379,36.17788 -30.39279,71.66285 -53.76332,101 -9.60072,12.05183 -39.15288,41.69975 -50.12109,50.2835 -8.39771,6.57207 -29.89941,21.24373 -37.40595,25.52392 -6.59963,3.76307 -29.39033,15.01323 -37.64935,18.58483 -16.83076,7.27842 -50.42453,16.86468 -66.85065,19.07638 -4.4,0.59244 -10.7,1.51105 -14,2.04136 -20.26454,3.25648 -46.67125,3.80064 -66,1.36004 z M 406.51148,467.13372 c 5.69934,-2.58913 143.0089,-139.86753 145.59545,-145.56241 2.30822,-5.08207 2.41076,-12.67811 0.23308,-17.26722 -2.52185,-5.3144 -140.5956,-143.06181 -145.7448,-145.40032 -17.81577,-8.09106 -35.87454,10.99046 -26.92624,28.4512 0.88648,1.72977 28.8861,30.46544 62.2214,63.85705 33.3353,33.39161 60.60963,61.19681 60.60963,61.78933 0,0.59253 -27.27884,28.39712 -60.61964,61.78799 -33.3408,33.39086 -61.34043,62.12592 -62.2214,63.85569 -8.88471,17.44501 9.11837,36.54506 26.85252,28.48869 z");
    pathSig.setAttribute("fill", "currentColor");

    //Coloco el path dentro del svg y el svg dentro del boton
    svgSig.appendChild(pathSig);
    botonSig.appendChild(svgSig);


    //Creo el titulo
    let titulo = document.createElement("h4");
    titulo.textContent = item.title;

    //Creo la descripcion
    let desc = document.createElement("p");
    desc.textContent = item.desc;

    //Creo el año
    let year = document.createElement("p");
    year.textContent = item.year;

    //Creo el div de las tecnologias
    let divTecnologias = document.createElement("div");
    divTecnologias.classList.add("tecnologiasProyecto");

    //Creo el link a github
    let githubLink = document.createElement("a");
    githubLink.href = item.github;
    githubLink.target = "_blank";

    //Creo la imagen de github
    let githubImagen = document.createElement("img");
    githubImagen.src = `img/logos/githubLogo${getModoTexto()}.svg`;
    githubImagen.alt = "Github";
    githubImagen.classList.add("githubProyecto");

    //Agrego la imagen al link
    githubLink.appendChild(githubImagen);

    //Agrego los botones, las imagenes y los puntos al carrusel
    carrusel.appendChild(botonAnt);
    carrusel.appendChild(contenedorImagenes);
    carrusel.appendChild(contenedorPuntos);
    carrusel.appendChild(botonSig);

    //Agrego todo al div general
    divGeneral.appendChild(carrusel);
    divGeneral.appendChild(titulo);
    divGeneral.appendChild(desc);
    divGeneral.appendChild(year);
    divGeneral.appendChild(divTecnologias);
    divGeneral.appendChild(githubLink);
    

    //Agrego el div general al contenedorTecnologias
    contenedorProyectos.appendChild(divGeneral);

  });

  insertarTecnologiasProyectos(proyectos, contenedorProyectos);
}

//Funcion que inserta las tecnologias del proyecto, le paso el proyecto y el contenedor donde se insertan
function insertarTecnologiasProyectos(proyectos, contenedorProyectos){

  //Inserto las tecnologias del proyecto
  proyectos.forEach((proyecto, index) => { //Recorro los proyectos y obtengo el indice

    //Obtengo el contenedor de las tecnologias como la etiqueta con la clase tecnologiasProyecto del hijo del contenedorProyectos del indice actual
    let contenedorTecnologias = contenedorProyectos.children[index].querySelector(".tecnologiasProyecto"); 
    contenedorTecnologias.replaceChildren();
    //Por cada tecnologia que tiene el proyecto actual
    proyecto.tecnologias.forEach(nombreTec => {
        //Obtengo la tecnologia del proyecto del arreglo de tecnologias
        let tec = tecnologias.find(t => t.name === nombreTec);
        if(tec){
          //Inserto la tecnologia

          //Creo el div que contiene la imagen y el texto
          let divGeneral = document.createElement("div");
          divGeneral.classList.add("tecnologiaProy");

          //Creo la imagen
          let imagen = document.createElement("img");
          imagen.src = `${tec.image}${getModoTexto()}.svg`;
          imagen.alt = tec.name;

          //Creo el texto
          let texto = document.createElement("p");
          texto.textContent = tec.name;

          //Agrego la imagen y el texto al div
          divGeneral.appendChild(imagen);
          divGeneral.appendChild(texto);

          //Agrego el div general al contenedorTecnologias
          contenedorTecnologias.appendChild(divGeneral);
        }
        

    });
  });
}

function inicializarCarruseles(){
  document.querySelectorAll(".carrusel").forEach(carrusel => {
    
    let imagenes = carrusel.querySelectorAll(".imagenesCarrusel img");
    let puntos = carrusel.querySelectorAll(".puntoImagen")
    let index = 0;

    let prev = carrusel.querySelector(".botonImgProyectoAnt");
    let next = carrusel.querySelector(".botonImgProyectoSig");

    prev.addEventListener("click", () => {
      imagenes[index].style.display = "none"; //No mostrar la imagen actual
      puntos[index].classList.remove("puntoActivo"); //Desactivar el punto actual
      index = (index - 1 + imagenes.length) % imagenes.length;
      imagenes[index].style.display = "block"; //Mostrar la anterior imagen
      puntos[index].classList.add("puntoActivo"); //Activar el anterior punto
    });

    next.addEventListener("click", () => {
      imagenes[index].style.display = "none"; //No mostrar la imagen actual
      puntos[index].classList.remove("puntoActivo"); //Desactivar el punto actual
      index = (index + 1) % imagenes.length;
      imagenes[index].style.display = "block"; //Mostrar la siguiente imagen
      puntos[index].classList.add("puntoActivo"); //Activar el siguiente punto
    });
  });
}

//Cargo el idioma seleccionado y luego llamo a cambiarTexto para insertarlo
function cargarIdioma(idioma) {
  if(idioma != idiomaActual){
    fetch(`json/${idioma}.json`).then(response => {
        if (response.ok) {
          response.json().then(data => {
            cambiarTexto(data);
            idiomaActual = idioma;
          });
        } else {
          throw Error(response.statusText);
        }
      })
  }
}


//Cambio el texto segun el idioma
function cambiarTexto(texto) {
  // Insertar textos simples
  document.title = texto.title;
  document.getElementById("descargarCV").textContent = texto.cv;
  document.getElementById("sobreMi").textContent = texto.sobreMi;
  document.getElementById("textoPresentacion").textContent = texto.presentacion;

  document.querySelectorAll(".tecnologias").forEach(item => {
    item.textContent = texto.tecnologias;
  });
  document.querySelectorAll(".textoProyectos").forEach(item => {
    item.textContent = texto.proyectos;
  });
  document.querySelectorAll(".estudios").forEach(item => {
    item.textContent = texto.estudios;
  });
  document.querySelectorAll(".contacto").forEach(item => {
    item.textContent = texto.contacto;
  });

  //Insertar proyectos
  proyectos = texto.proyectosLista;
  mostrarProyectos(proyectos);
  inicializarCarruseles();

  // Insertar lista de estudios
  const listaEstudios = document.getElementById("estudiosLista");
  listaEstudios.replaceChildren(); //Elimino los hijos de la lista para limpiarla
  texto.estudiosLista.forEach(item => {
    const li = document.createElement("li");
    li.textContent = item;
    listaEstudios.appendChild(li);
  });

  document.getElementById("textoContacto").textContent = texto.textoContacto;

}

botonEspañol.addEventListener("click", function(){
    cargarIdioma("es");
});

botonIngles.addEventListener("click", function(){
  cargarIdioma("en");
});


//Tecnologias
function cargarTecnologias(){
  fetch("json/tecnologias.json").then(response => {
      if (response.ok) {
        response.json().then(data => {
          tecnologias = data;
          mostrarTecnologias();
        });
      } else {
        throw Error(response.statusText);
      }
    })
}

function mostrarTecnologias(){

  let listaTecnologias = document.getElementById("tecnologiasLista");
    tecnologias.forEach(item => {
      //Creo el div que contiene la imagen y el texto
      let divGeneral = document.createElement("div");
      divGeneral.classList.add("tecnologia");

      //Creo la imagen
      let imagen = document.createElement("img");
      imagen.src = `${item.image}${getModoTexto()}.svg`;
      imagen.alt = item.name;

      //Creo el texto
      let texto = document.createElement("p");
      texto.textContent = item.name;

      //Agrego la imagen y el texto al div
      divGeneral.appendChild(imagen);
      divGeneral.appendChild(texto);

      //Agrego el div general a la listaTecnologias
      listaTecnologias.appendChild(divGeneral);
    });
}


//Modo Oscuro 
function actualizarModo(){
  //Cambio icono descarga CV
  let cv = document.getElementById("imagenCV");
  cv.src= `img/logos/flechaDescarga${getModoTexto()}.svg`;
  

  //Actualizo los logos de las tecnologias de cada proyecto
  let contenedorProyectos = document.getElementById("proyectosLista");
  insertarTecnologiasProyectos(proyectos, contenedorProyectos);

  //Actualizo icono github de cada proyecto
  let githubProyectosLogos = document.querySelectorAll(".githubProyecto");
  githubProyectosLogos.forEach(img => {
    img.src = `img/logos/githubLogo${getModoTexto()}.svg`;
  });


  //Actualizo los logos de las tecnologias
  let listaTecnologias = document.getElementById("tecnologiasLista");
  listaTecnologias.replaceChildren(); //Elimino los hijos que tenga la lista
  mostrarTecnologias();

  //Cambiar color letra y fondo
  document.body.classList.toggle("claro"); //Activo o desactivo la clase claro al body

  //Cambiar iconos contacto
  let gmail = document.getElementById("gmailLogo");
  gmail.src= `img/logos/gmailLogo${getModoTexto()}.svg`;

   let github = document.getElementById("github");
   github.src= `img/logos/githubLogo${getModoTexto()}.svg`;

   let linkedin = document.getElementById("linkedin");
   linkedin.src= `img/logos/linkedinLogo${getModoTexto()}.svg`;
}

//Boton para cambiar el modo
const botonModoOscuro = document.getElementById("modoOscuro");

botonModoOscuro.addEventListener("click", function(){
  botonModoOscuro.classList.toggle("activo"); //Activar o desactivar la clase activo al boton
  modoOscuro = !modoOscuro;
  actualizarModo();
});


//Muestro las tecnologias 1 sola vez
cargarTecnologias();

// Cargar español al inicio
cargarIdioma("es");


botonMenu = document.getElementById("botonMenu");

botonMenu.addEventListener("click", function(){
  document.getElementById("botonEncabezado").classList.toggle('show'); //Activar o desactivar la clase show
});