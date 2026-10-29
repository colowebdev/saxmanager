"""
Conexión a SQLite.

- En local la base vive en database/saxofones.db
- En Vercel el sistema de archivos del proyecto es de solo lectura, así que
  copiamos la base a /tmp (la única carpeta donde se puede escribir).
"""
import os
import shutil
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_DIR = BASE_DIR / "database"
DB_ORIGINAL = DB_DIR / "saxofones.db"

# Vercel define la variable de entorno VERCEL=1
if os.environ.get("VERCEL"):
    DB_PATH = Path("/tmp/saxofones.db")
else:
    DB_PATH = DB_ORIGINAL


def crear_base_si_no_existe() -> None:
    """Crea la base con schema.sql + seed.sql si todavía no existe."""
    if DB_PATH.exists():
        return

    # En Vercel: si venía una base ya creada en el repo, la copiamos a /tmp
    if DB_PATH != DB_ORIGINAL and DB_ORIGINAL.exists():
        shutil.copy(DB_ORIGINAL, DB_PATH)
        return

    conn = sqlite3.connect(DB_PATH)
    conn.executescript((DB_DIR / "schema.sql").read_text(encoding="utf-8"))
    conn.executescript((DB_DIR / "seed.sql").read_text(encoding="utf-8"))
    conn.commit()
    conn.close()


def get_conexion() -> sqlite3.Connection:
    """Devuelve una conexión lista para usar.

    row_factory = sqlite3.Row permite convertir cada fila en dict(fila).
    PRAGMA foreign_keys = ON hace que SQLite respete las llaves foráneas
    (por defecto viene apagado).
    """
    crear_base_si_no_existe()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def get_db():
    """Dependencia de FastAPI: abre la conexión y la cierra al terminar."""
    conn = get_conexion()
    try:
        yield conn
    finally:
        conn.close()
