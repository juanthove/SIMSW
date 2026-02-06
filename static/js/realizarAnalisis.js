const urlInput = document.getElementById("url");
const boton = document.getElementById("botonScan");
const botonPrueba = document.getElementById("botonPrueba");
const resultado = document.getElementById("resultado");

const token = localStorage.getItem("token");
import { apiFetch } from "./api.js";

document.addEventListener("DOMContentLoaded", function(){

    //Redirigir a login si no existe un token
    
    if (!token) {
        window.location.href = "/login";
    }



    boton.addEventListener("click", async () => {

    const url = urlInput.value.trim();
    if (!url) { resultado.textContent = "Por favor ingrese una URL."; return; }
    resultado.textContent = "Analizando...";

    try {
        const res = await fetch('/analizarEstatico', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url })
        });

        // Loguear status y headers
        console.log("HTTP status:", res.status, res.statusText);

        const text = await res.text(); // leer raw
        console.log("Raw response text:", text);

        let data;
        try {
            data = JSON.parse(text);
        } catch (e) {
            resultado.textContent = "Respuesta no JSON:";
            console.error("No se pudo parsear JSON:", e);
            return;
        }

        console.log("Parsed JSON:", data);

        if (data.error) {
            resultado.textContent = "Error del servidor: " + (data.detail ? data.detail : data.error);
            return;
        }

        if (!Array.isArray(data.resultado) || data.resultado.length === 0) {
            resultado.textContent = `No se obtuvieron fragments o resultado vacío. JSON completo: ${JSON.stringify(data)}`;
            return;
        }

        // Mostrar bonito y crudo también
        let out = `URL analizada: ${data.url}\n\n`;
        data.resultado.forEach(r => {
            out += `Fragmento ${r.fragment} [${r.type}]: ${r.label} (${r.confidence})\n`;
            out += `--- Código ---\n${r.code_fragment || ""}\n\n`;
        });

        resultado.textContent = out;
    } catch (err) {
        console.error("Fetch error:", err);
        resultado.textContent = "Error al conectar con el servidor: " + err;
    }


    });

    botonPrueba.addEventListener("click", async () => {
        const res = await apiFetch("/analizarAlteraciones", {
              method: "POST",
              body: JSON.stringify({
                url: "https://juanthove.github.io/proyecto_DW_grupo3/",
                sitio_web_id: 30
              })
            });
            
        const data = await res.json();
        console.log(data);
        
    })



});

