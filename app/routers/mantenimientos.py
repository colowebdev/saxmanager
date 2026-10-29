import sqlite3

from fastapi import APIRouter, Depends

from app.database import get_db
from app.errores import error_integridad, no_encontrado
from app.schemas import MantenimientoIn

router = APIRouter(prefix="/api/mantenimientos", tags=["Mantenimientos"])

# Doble JOIN: trae el saxofón (con su marca) y el cliente de cada servicio
SELECT_MANT = """
    SELECT mt.*,
           c.nombre AS cliente,
           ma.nombre || ' ' || s.modelo || ' (' || s.numero_serie || ')' AS saxofon
    FROM mantenimientos mt
    JOIN saxofones s  ON s.id  = mt.saxofon_id
    JOIN marcas    ma ON ma.id = s.marca_id
    JOIN clientes  c  ON c.id  = mt.cliente_id
"""


def _valores(m: MantenimientoIn):
    return (m.saxofon_id, m.cliente_id, m.fecha.isoformat(), m.descripcion, m.costo, m.estado)


@router.get("")
def listar_mantenimientos(db: sqlite3.Connection = Depends(get_db)):
    filas = db.execute(SELECT_MANT + " ORDER BY mt.fecha DESC, mt.id DESC").fetchall()
    return [dict(f) for f in filas]


@router.get("/{mant_id}")
def obtener_mantenimiento(mant_id: int, db: sqlite3.Connection = Depends(get_db)):
    fila = db.execute(SELECT_MANT + " WHERE mt.id = ?", (mant_id,)).fetchone()
    if fila is None:
        raise no_encontrado("Mantenimiento", mant_id)
    return dict(fila)


@router.post("", status_code=201)
def crear_mantenimiento(m: MantenimientoIn, db: sqlite3.Connection = Depends(get_db)):
    try:
        cur = db.execute(
            """INSERT INTO mantenimientos
               (saxofon_id, cliente_id, fecha, descripcion, costo, estado)
               VALUES (?, ?, ?, ?, ?, ?)""",
            _valores(m),
        )
        db.commit()
    except sqlite3.IntegrityError as e:
        raise error_integridad(e)
    return obtener_mantenimiento(cur.lastrowid, db)


@router.put("/{mant_id}")
def actualizar_mantenimiento(mant_id: int, m: MantenimientoIn, db: sqlite3.Connection = Depends(get_db)):
    try:
        cur = db.execute(
            """UPDATE mantenimientos
               SET saxofon_id = ?, cliente_id = ?, fecha = ?, descripcion = ?, costo = ?, estado = ?
               WHERE id = ?""",
            _valores(m) + (mant_id,),
        )
        db.commit()
    except sqlite3.IntegrityError as e:
        raise error_integridad(e)
    if cur.rowcount == 0:
        raise no_encontrado("Mantenimiento", mant_id)
    return obtener_mantenimiento(mant_id, db)


@router.delete("/{mant_id}")
def eliminar_mantenimiento(mant_id: int, db: sqlite3.Connection = Depends(get_db)):
    cur = db.execute("DELETE FROM mantenimientos WHERE id = ?", (mant_id,))
    db.commit()
    if cur.rowcount == 0:
        raise no_encontrado("Mantenimiento", mant_id)
    return {"mensaje": "Mantenimiento eliminado"}
