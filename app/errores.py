"""Traduce los errores de SQLite a respuestas HTTP entendibles."""
import sqlite3

from fastapi import HTTPException


def no_encontrado(recurso: str, id_: int) -> HTTPException:
    return HTTPException(status_code=404, detail=f"{recurso} con id {id_} no existe")


def error_integridad(e: sqlite3.IntegrityError, al_borrar: bool = False) -> HTTPException:
    msg = str(e)
    if "UNIQUE" in msg:
        campo = msg.split(".")[-1]
        return HTTPException(status_code=409, detail=f"Ya existe un registro con ese valor de '{campo}'")
    if "FOREIGN KEY" in msg:
        if al_borrar:
            return HTTPException(
                status_code=409,
                detail="No se puede eliminar: hay otros registros que dependen de este",
            )
        return HTTPException(status_code=400, detail="El registro relacionado (marca, saxofón o cliente) no existe")
    return HTTPException(status_code=400, detail=f"Dato inválido: {msg}")
