import sqlite3

from fastapi import APIRouter, Depends

from app.database import get_db
from app.errores import error_integridad, no_encontrado
from app.schemas import ClienteIn

router = APIRouter(prefix="/api/clientes", tags=["Clientes"])


@router.get("")
def listar_clientes(db: sqlite3.Connection = Depends(get_db)):
    filas = db.execute("""
        SELECT c.*, COUNT(mt.id) AS total_servicios
        FROM clientes c
        LEFT JOIN mantenimientos mt ON mt.cliente_id = c.id
        GROUP BY c.id
        ORDER BY c.nombre
    """).fetchall()
    return [dict(f) for f in filas]


@router.get("/{cliente_id}")
def obtener_cliente(cliente_id: int, db: sqlite3.Connection = Depends(get_db)):
    fila = db.execute("SELECT * FROM clientes WHERE id = ?", (cliente_id,)).fetchone()
    if fila is None:
        raise no_encontrado("Cliente", cliente_id)
    return dict(fila)


@router.post("", status_code=201)
def crear_cliente(cliente: ClienteIn, db: sqlite3.Connection = Depends(get_db)):
    cur = db.execute(
        "INSERT INTO clientes (nombre, telefono, correo) VALUES (?, ?, ?)",
        (cliente.nombre, cliente.telefono, cliente.correo),
    )
    db.commit()
    return obtener_cliente(cur.lastrowid, db)


@router.put("/{cliente_id}")
def actualizar_cliente(cliente_id: int, cliente: ClienteIn, db: sqlite3.Connection = Depends(get_db)):
    cur = db.execute(
        "UPDATE clientes SET nombre = ?, telefono = ?, correo = ? WHERE id = ?",
        (cliente.nombre, cliente.telefono, cliente.correo, cliente_id),
    )
    db.commit()
    if cur.rowcount == 0:
        raise no_encontrado("Cliente", cliente_id)
    return obtener_cliente(cliente_id, db)


@router.delete("/{cliente_id}")
def eliminar_cliente(cliente_id: int, db: sqlite3.Connection = Depends(get_db)):
    # ON DELETE RESTRICT: si el cliente tiene servicios, SQLite no deja borrarlo
    try:
        cur = db.execute("DELETE FROM clientes WHERE id = ?", (cliente_id,))
        db.commit()
    except sqlite3.IntegrityError as e:
        raise error_integridad(e, al_borrar=True)
    if cur.rowcount == 0:
        raise no_encontrado("Cliente", cliente_id)
    return {"mensaje": "Cliente eliminado"}
