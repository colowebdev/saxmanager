// =========================================================
// app.js — Lógica de la interfaz
// Cada sección (recurso) se describe en CONFIG: qué columnas
// mostrar en la tabla y qué campos tiene su formulario.
// =========================================================

const TIPOS = ["Soprano", "Alto", "Tenor", "Barítono"];
const ESTADOS_SAX = ["Disponible", "Reservado", "En mantenimiento", "Vendido"];
const ESTADOS_MANT = ["Pendiente", "En proceso", "Terminado"];

// ---------- utilidades ----------
const $ = (sel) => document.querySelector(sel);

function esc(valor) {
  // Evita que texto guardado en la BD se interprete como HTML
  return String(valor ?? "").replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}
const dinero = (n) => "$" + Number(n || 0).toLocaleString("es-CR", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const badge = (texto) => `<span class="badge b-${esc(texto).toLowerCase().replace(/\s+/g, "-")}">${esc(texto)}</span>`;

function toast(msg, tipo = "ok") {
  const t = $("#toast");
  t.textContent = msg;
  t.className = `visible ${tipo}`;
  clearTimeout(t._timer);
  t._timer = setTimeout(() => (t.className = ""), 3000);
}

// ---------- configuración de cada recurso ----------
const CONFIG = {
  saxofones: {
    singular: "saxofón",
    columnas: [
      ["Marca", (s) => esc(s.marca)],
      ["Modelo", (s) => `<strong>${esc(s.modelo)}</strong>`],
      ["Tipo", (s) => esc(s.tipo)],
      ["N.º serie", (s) => `<code>${esc(s.numero_serie)}</code>`],
      ["Año", (s) => esc(s.anio ?? "—")],
      ["Precio", (s) => dinero(s.precio)],
      ["Estado", (s) => badge(s.estado)],
    ],
    campos: async () => [
      { nombre: "marca_id", etiqueta: "Marca", tipo: "select", opciones: await opcionesDe("marcas", (m) => m.nombre), requerido: true },
      { nombre: "modelo", etiqueta: "Modelo", requerido: true },
      { nombre: "tipo", etiqueta: "Tipo", tipo: "select", opciones: TIPOS.map((t) => [t, t]), requerido: true },
      { nombre: "numero_serie", etiqueta: "Número de serie", requerido: true },
      { nombre: "acabado", etiqueta: "Acabado" },
      { nombre: "anio", etiqueta: "Año de fabricación", tipo: "number", min: 1840, max: 2100 },
      { nombre: "precio", etiqueta: "Precio (USD)", tipo: "number", step: "0.01", min: 0, requerido: true },
      { nombre: "estado", etiqueta: "Estado", tipo: "select", opciones: ESTADOS_SAX.map((e) => [e, e]), requerido: true, defecto: "Disponible" },
    ],
    query: () => {
      const p = new URLSearchParams();
      if ($("#f-buscar").value) p.set("buscar", $("#f-buscar").value);
      if ($("#f-tipo").value) p.set("tipo", $("#f-tipo").value);
      if ($("#f-estado").value) p.set("estado", $("#f-estado").value);
      const s = p.toString();
      return s ? `?${s}` : "";
    },
  },

  marcas: {
    singular: "marca",
    columnas: [
      ["Nombre", (m) => `<strong>${esc(m.nombre)}</strong>`],
      ["País", (m) => esc(m.pais ?? "—")],
      ["Saxofones", (m) => esc(m.total_saxofones)],
    ],
    campos: async () => [
      { nombre: "nombre", etiqueta: "Nombre", requerido: true },
      { nombre: "pais", etiqueta: "País de origen" },
    ],
  },

  clientes: {
    singular: "cliente",
    columnas: [
      ["Nombre", (c) => `<strong>${esc(c.nombre)}</strong>`],
      ["Teléfono", (c) => esc(c.telefono ?? "—")],
      ["Correo", (c) => esc(c.correo ?? "—")],
      ["Servicios", (c) => esc(c.total_servicios)],
    ],
    campos: async () => [
      { nombre: "nombre", etiqueta: "Nombre completo", requerido: true },
      { nombre: "telefono", etiqueta: "Teléfono" },
      { nombre: "correo", etiqueta: "Correo electrónico", tipo: "email" },
    ],
  },

  mantenimientos: {
    singular: "servicio",
    columnas: [
      ["Fecha", (m) => esc(m.fecha)],
      ["Saxofón", (m) => esc(m.saxofon)],
      ["Cliente", (m) => esc(m.cliente)],
      ["Descripción", (m) => esc(m.descripcion)],
      ["Costo", (m) => dinero(m.costo)],
      ["Estado", (m) => badge(m.estado)],
    ],
    campos: async () => [
      { nombre: "saxofon_id", etiqueta: "Saxofón", tipo: "select", requerido: true,
        opciones: await opcionesDe("saxofones", (s) => `${s.marca} ${s.modelo} (${s.numero_serie})`) },
      { nombre: "cliente_id", etiqueta: "Cliente", tipo: "select", requerido: true,
        opciones: await opcionesDe("clientes", (c) => c.nombre) },
      { nombre: "fecha", etiqueta: "Fecha", tipo: "date", requerido: true },
      { nombre: "descripcion", etiqueta: "Trabajo realizado", tipo: "textarea", requerido: true },
      { nombre: "costo", etiqueta: "Costo (USD)", tipo: "number", step: "0.01", min: 0, requerido: true },
      { nombre: "estado", etiqueta: "Estado", tipo: "select", opciones: ESTADOS_MANT.map((e) => [e, e]), requerido: true, defecto: "Pendiente" },
    ],
  },
};

// Las listas desplegables (marcas, clientes, saxofones) también salen de la BD
async function opcionesDe(recurso, texto) {
  const lista = await api.listar(recurso);
  return lista.map((x) => [x.id, texto(x)]);
}

// ---------- tablas ----------
function pintarTabla(tabla, columnas, filas, recurso) {
  if (filas.length === 0) {
    tabla.innerHTML = `<tr><td class="vacio">No hay registros todavía.</td></tr>`;
    return;
  }
  const head = columnas.map(([t]) => `<th>${t}</th>`).join("") + (recurso ? "<th></th>" : "");
  const body = filas.map((f) => {
    const celdas = columnas.map(([, fn]) => `<td>${fn(f)}</td>`).join("");
    const acciones = recurso
      ? `<td class="acc">
           <button class="btn mini" onclick="abrirFormulario('${recurso}', ${f.id})">Editar</button>
           <button class="btn mini peligro" onclick="eliminar('${recurso}', ${f.id})">Eliminar</button>
         </td>`
      : "";
    return `<tr>${celdas}${acciones}</tr>`;
  }).join("");
  tabla.innerHTML = `<thead><tr>${head}</tr></thead><tbody>${body}</tbody>`;
}

async function cargar(recurso) {
  const cfg = CONFIG[recurso];
  const tabla = $(`#tabla-${recurso}`);
  try {
    const datos = await api.listar(recurso, cfg.query ? cfg.query() : "");
    pintarTabla(tabla, cfg.columnas, datos, recurso);
  } catch (e) {
    tabla.innerHTML = `<tr><td class="vacio">Error al cargar: ${esc(e.message)}</td></tr>`;
  }
}

async function cargarInicio() {
  try {
    const r = await api.listar("saxofones/resumen");
    const e = r.por_estado;
    $("#tarjetas-resumen").innerHTML = [
      ["Saxofones registrados", r.total_saxofones],
      ["Disponibles", e["Disponible"] || 0],
      ["En el taller", e["En mantenimiento"] || 0],
      ["Servicios activos", r.mantenimientos_activos],
      ["Valor del inventario", dinero(r.valor_inventario)],
    ].map(([t, v]) => `<div class="tarjeta"><span>${t}</span><strong>${v}</strong></div>`).join("");

    const ultimos = (await api.listar("mantenimientos")).slice(0, 5);
    pintarTabla($("#tabla-ultimos"), CONFIG.mantenimientos.columnas, ultimos, null);
  } catch (err) {
    $("#tarjetas-resumen").innerHTML = `<p class="error">No se pudo conectar con la API: ${esc(err.message)}</p>`;
  }
}

// ---------- formulario (crear / editar) ----------
let edicion = { recurso: null, id: null };

function htmlCampo(c, valor) {
  const v = valor ?? "";
  const req = c.requerido ? "required" : "";
  let input;
  if (c.tipo === "select") {
    const ops = c.opciones.map(([val, txt]) =>
      `<option value="${esc(val)}" ${String(val) === String(v) ? "selected" : ""}>${esc(txt)}</option>`).join("");
    input = `<select name="${c.nombre}" ${req}><option value="">— Seleccione —</option>${ops}</select>`;
  } else if (c.tipo === "textarea") {
    input = `<textarea name="${c.nombre}" rows="3" ${req}>${esc(v)}</textarea>`;
  } else {
    const extra = ["min", "max", "step"].filter((k) => c[k] !== undefined).map((k) => `${k}="${c[k]}"`).join(" ");
    input = `<input name="${c.nombre}" type="${c.tipo || "text"}" value="${esc(v)}" ${extra} ${req}>`;
  }
  return `<label>${c.etiqueta}${c.requerido ? " *" : ""}${input}</label>`;
}

async function abrirFormulario(recurso, id = null) {
  const cfg = CONFIG[recurso];
  edicion = { recurso, id };
  $("#modal-error").textContent = "";
  $("#modal-titulo").textContent = (id ? "Editar " : "Nuevo ") + cfg.singular;

  try {
    const [campos, actual] = await Promise.all([
      cfg.campos(),
      id ? api.obtener(recurso, id) : Promise.resolve({}),
    ]);
    if (!id && recurso === "mantenimientos") actual.fecha = new Date().toISOString().slice(0, 10);
    // En registros nuevos se usa el valor por defecto del campo (si tiene)
    $("#modal-campos").innerHTML = campos.map((c) => htmlCampo(c, actual[c.nombre] ?? c.defecto)).join("");
    $("#modal").showModal();
  } catch (e) {
    toast(e.message, "error");
  }
}

function cerrarModal() {
  $("#modal").close();
}

$("#formulario").addEventListener("submit", async (ev) => {
  ev.preventDefault();
  const { recurso, id } = edicion;

  // Convierte el formulario a objeto: vacíos -> null, números -> Number
  const datos = {};
  for (const el of ev.target.querySelectorAll("[name]")) {
    let v = el.value.trim();
    if (v === "") v = null;
    else if (el.type === "number" || el.name.endsWith("_id")) v = Number(v);
    datos[el.name] = v;
  }

  try {
    if (id) await api.actualizar(recurso, id, datos);
    else await api.crear(recurso, datos);
    cerrarModal();
    toast(id ? "Cambios guardados" : "Registro creado");
    cargar(recurso);
  } catch (e) {
    $("#modal-error").textContent = e.message;
  }
});

async function eliminar(recurso, id) {
  const aviso = recurso === "saxofones" ? "\nTambién se borrarán sus servicios de taller." : "";
  if (!confirm(`¿Seguro que desea eliminar este ${CONFIG[recurso].singular}?${aviso}`)) return;
  try {
    await api.eliminar(recurso, id);
    toast("Registro eliminado");
    cargar(recurso);
  } catch (e) {
    toast(e.message, "error");
  }
}

// ---------- navegación ----------
function mostrarVista(nombre) {
  document.querySelectorAll(".tab").forEach((b) => b.classList.toggle("activo", b.dataset.vista === nombre));
  document.querySelectorAll(".vista").forEach((v) => v.classList.toggle("activa", v.id === `vista-${nombre}`));
  if (nombre === "inicio") cargarInicio();
  else cargar(nombre);
}

document.querySelectorAll(".tab").forEach((b) => b.addEventListener("click", () => mostrarVista(b.dataset.vista)));

// Filtros de saxofones: recargan la tabla al escribir/cambiar
let espera;
$("#f-buscar").addEventListener("input", () => { clearTimeout(espera); espera = setTimeout(() => cargar("saxofones"), 300); });
$("#f-tipo").addEventListener("change", () => cargar("saxofones"));
$("#f-estado").addEventListener("change", () => cargar("saxofones"));

mostrarVista("inicio");
