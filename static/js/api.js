//Para hacer fetch a los endpoints utilizando el token
export async function apiFetch(url, options = {}) {
  const token = localStorage.getItem("token");

  const headers = options.body instanceof FormData
    ? { ...(options.headers || {}) }   //NO Content-Type
    : {
        "Content-Type": "application/json",
        ...(options.headers || {})
      };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(url, {
    ...options,
    headers
  });

  //Token inválido o expirado
  if (response.status === 401 || response.status === 403) {
    localStorage.removeItem("token");
    window.location.href = "/login";
    return;
  }

  return response;
}
