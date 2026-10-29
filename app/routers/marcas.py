import sqlite3

from fastapi import APIRouter, Depends

from app.database import get_db
from app.errores import error_integridad, no_encontrado
from app.schemas import MarcaIn

router = APIRouter(prefix="/api/marcas", tags=["Marcas"])


@router.get("")
def listar_marcas(db: sqlite3.Connection = Depends(get_db)):
    # Incluye cuántos saxofones tiene cada marca (LEFT JOIN para contar también las que tienen 0)
    filas = db.execute("""
        SELECT m.id, m.nombre, m.pais, COUNT(s.id) AS total_saxofones
        FROM marcas m
        LEFT JOIN saxofones s ON s.marca_id = m.id
        GROUP BY m.id
        ORDER BY m.nombre
    """).fetchall()
    return [dict(f) for f in filas]


@router.get("/{marca_id}")
def obtener_marca(marca_id: int, db: sqlite3.Connection = Depends(get_db)):
    fila = db.execute("SELECT * FROM marcas WHERE id = ?", (marca_id,)).fetchone()
    if fila is None:
        raise no_encontrado("Marca", marca_id)
    return dict(fila)


@router.post("", status_code=201)
def crear_marca(marca: MarcaIn, db: sqlite3.Connection = Depends(get_db)):
    try:
        cur = db.execute("INSERT INTO marcas (nombre, pais) VALUES (?, ?)", (marca.nombre, marca.pais))
        db.commit()
    except sqlite3.IntegrityError as e:
        raise error_integridad(e)
    return obtener_marca(cur.lastrowid, db)


@router.put("/{marca_id}")
def actualizar_marca(marca_id: int, marca: MarcaIn, db: sqlite3.Connection = Depends(get_db)):
    try:
        cur = db.execute(
            "UPDATE marcas SET nombre = ?, pais = ? WHERE id = ?",
            (marca.nombre, marca.pais, marca_id),
        )
        db.commit()
    except sqlite3.IntegrityError as e:
        raise error_integridad(e)
    if cur.rowcount == 0:
        raise no_encontrado("Marca", marca_id)
    return obtener_marca(marca_id, db)


@router.delete("/{marca_id}")
def eliminar_marca(marca_id: int, db: sqlite3.Connection = Depends(get_db)):
    try:
        cur = db.execute("DELETE FROM marcas WHERE id = ?", (marca_id,))
        db.commit()
    except sqlite3.IntegrityError as e:
        raise error_integridad(e, al_borrar=True)
    if cur.rowcount == 0:
        raise no_encontrado("Marca", marca_id)
    return {"mensaje": "Marca eliminada"}
