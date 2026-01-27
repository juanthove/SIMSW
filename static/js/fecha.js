export function formatearFecha(fechaISO) {
  if (!fechaISO) return "-";

  return new Date(fechaISO).toLocaleString("es-UY", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false
  }).replace(",", "");
}

export function formatearFechaDia(fechaISO) {
  if (!fechaISO) return null;

  return new Date(fechaISO).toLocaleDateString("es-UY", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric"
  });
}
