import sqlite3
from typing import Optional

from fastapi import APIRouter, Depends

from app.database import get_db
from app.errores import error_integridad, no_encontrado
from app.schemas import SaxofonIn

router = APIRouter(prefix="/api/saxofones", tags=["Saxofones"])

# JOIN con marcas para devolver también el nombre de la marca
SELECT_SAX = """
    SELECT s.*, m.nombre AS marca
    FROM saxofones s
    JOIN marcas m ON m.id = s.marca_id
"""


@router.get("")
def listar_saxofones(
    tipo: Optional[str] = None,
    estado: Optional[str] = None,
    buscar: Optional[str] = None,
    db: sqlite3.Connection = Depends(get_db),
):
    """Lista con filtros opcionales: /api/saxofones?tipo=Alto&estado=Disponible&buscar=yamaha"""
    condiciones, params = [], []
    if tipo:
        condiciones.append("s.tipo = ?")
        params.append(tipo)
    if estado:
        condiciones.append("s.estado = ?")
        params.append(estado)
    if buscar:
        condiciones.append("(s.modelo LIKE ? OR s.numero_serie LIKE ? OR m.nombre LIKE ?)")
        params += [f"%{buscar}%"] * 3

    sql = SELECT_SAX
    if condiciones:
        sql += " WHERE " + " AND ".join(condiciones)
    sql += " ORDER BY s.id DESC"

    return [dict(f) for f in db.execute(sql, params).fetchall()]


@router.get("/resumen")
def resumen(db: sqlite3.Connection = Depends(get_db)):
    """Datos para las tarjetas del inicio."""
    por_estado = db.execute(
        "SELECT estado, COUNT(*) AS total FROM saxofones GROUP BY estado"
    ).fetchall()
    valor = db.execute(
        "SELECT COALESCE(SUM(precio), 0) FROM saxofones WHERE estado != 'Vendido'"
    ).fetchone()[0]
    pendientes = db.execute(
        "SELECT COUNT(*) FROM mantenimientos WHERE estado != 'Terminado'"
    ).fetchone()[0]
    total = db.execute("SELECT COUNT(*) FROM saxofones").fetchone()[0]
    return {
        "total_saxofones": total,
        "por_estado": {f["estado"]: f["total"] for f in por_estado},
        "valor_inventario": valor,
        "mantenimientos_activos": pendientes,
    }


@router.get("/{sax_id}")
def obtener_saxofon(sax_id: int, db: sqlite3.Connection = Depends(get_db)):
    fila = db.execute(SELECT_SAX + " WHERE s.id = ?", (sax_id,)).fetchone()
    if fila is None:
        raise no_encontrado("Saxofón", sax_id)
    return dict(fila)


@router.post("", status_code=201)
def crear_saxofon(sax: SaxofonIn, db: sqlite3.Connection = Depends(get_db)):
    try:
        cur = db.execute(
            """INSERT INTO saxofones
               (marca_id, modelo, tipo, numero_serie, acabado, anio, precio, estado)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (sax.marca_id, sax.modelo, sax.tipo, sax.numero_serie,
             sax.acabado, sax.anio, sax.precio, sax.estado),
        )
        db.commit()
    except sqlite3.IntegrityError as e:
        raise error_integridad(e)
    return obtener_saxofon(cur.lastrowid, db)


@router.put("/{sax_id}")
def actualizar_saxofon(sax_id: int, sax: SaxofonIn, db: sqlite3.Connection = Depends(get_db)):
    try:
        cur = db.execute(
            """UPDATE saxofones
               SET marca_id = ?, modelo = ?, tipo = ?, numero_serie = ?,
                   acabado = ?, anio = ?, precio = ?, estado = ?
               WHERE id = ?""",
            (sax.marca_id, sax.modelo, sax.tipo, sax.numero_serie,
             sax.acabado, sax.anio, sax.precio, sax.estado, sax_id),
        )
        db.commit()
    except sqlite3.IntegrityError as e:
        raise error_integridad(e)
    if cur.rowcount == 0:
        raise no_encontrado("Saxofón", sax_id)
    return obtener_saxofon(sax_id, db)


@router.delete("/{sax_id}")
def eliminar_saxofon(sax_id: int, db: sqlite3.Connection = Depends(get_db)):
    # ON DELETE CASCADE: se borran también sus mantenimientos
    cur = db.execute("DELETE FROM saxofones WHERE id = ?", (sax_id,))
    db.commit()
    if cur.rowcount == 0:
        raise no_encontrado("Saxofón", sax_id)
    return {"mensaje": "Saxofón eliminado"}
