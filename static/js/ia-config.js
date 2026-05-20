import { apiFetch } from "./api.js";

const form = document.getElementById("formIA");

const radioGemini = document.querySelector('input[value="gemini"]');
const radioGroq = document.querySelector('input[value="groq"]');
const radioOllama = document.querySelector('input[value="ollama"]');

const inputGeminiKey = document.getElementById("geminiKey");
const inputGroqKey = document.getElementById("groqKey");

const MODELOS = {
  gemini: "gemini-2.5-flash",
  groq: "llama-3.3-70b-versatile",
  ollama: "ollama-local",
};

//Cargar configuración
cargarConfiguracion();

async function cargarConfiguracion() {
  try {
    const response = await apiFetch("/config/ia");

    if (!response.ok) {
      throw new Error("Error al cargar configuración");
    }

    const data = await response.json();

    //Modelo seleccionado
    switch (data.MODEL) {
      case MODELOS.groq:
        radioGroq.checked = true;
        break;

      case MODELOS.ollama:
        radioOllama.checked = true;
        break;

      default:
        radioGemini.checked = true;
        break;
    }

    //Keys
    inputGeminiKey.value = data.GOOGLE_API_KEY || "";
    inputGroqKey.value = data.GROQ_API_KEY || "";
  } catch (err) {
    console.error(err);
    displayToast("Error al cargar configuración", "error");
  }
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

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  let modelo = MODELOS.gemini;

  if (radioGroq.checked) {
    modelo = MODELOS.groq;
  }

  if (radioOllama.checked) {
    modelo = MODELOS.ollama;
  }

  const payload = {
    MODEL: modelo,
    GOOGLE_API_KEY: inputGeminiKey.value.trim(),
    GROQ_API_KEY: inputGroqKey.value.trim(),
  };

  try {
    const response = await apiFetch("/config/ia", {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || "Error al guardar configuración");
    }

    displayToast("Configuración guardada correctamente", "success");
  } catch (err) {
    console.error(err);
    displayToast(err.message, "error");
  }
});
