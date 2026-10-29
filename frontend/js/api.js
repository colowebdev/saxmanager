// =========================================================
// api.js — Toda la comunicación con FastAPI pasa por aquí
// =========================================================

// Si el frontend se sirve desde FastAPI (local o Vercel) basta con "".
// Si lo abrís con Live Server, cambiá a "http://127.0.0.1:8000".
const API_URL = "";

async function peticion(ruta, metodo = "GET", datos = null) {
  const opciones = { method: metodo, headers: { "Content-Type": "application/json" } };
  if (datos) opciones.body = JSON.stringify(datos);

  const resp = await fetch(`${API_URL}/api/${ruta}`, opciones);
  const json = await resp.json().catch(() => ({}));

  if (!resp.ok) {
    // FastAPI devuelve { detail: "texto" } o, en errores 422, { detail: [ {msg, loc}, ... ] }
    let msg = json.detail || `Error ${resp.status}`;
    if (Array.isArray(msg)) msg = msg.map((e) => `${e.loc.at(-1)}: ${e.msg}`).join(" · ");
    throw new Error(msg);
  }
  return json;
}

const api = {
  listar:     (recurso, query = "") => peticion(`${recurso}${query}`),
  obtener:    (recurso, id)         => peticion(`${recurso}/${id}`),
  crear:      (recurso, datos)      => peticion(recurso, "POST", datos),
  actualizar: (recurso, id, datos)  => peticion(`${recurso}/${id}`, "PUT", datos),
  eliminar:   (recurso, id)         => peticion(`${recurso}/${id}`, "DELETE"),
};
