"""
Modelos Pydantic: validan los datos que llegan en POST/PUT.
Si algo no cumple (ej. precio negativo o tipo inválido) FastAPI
responde automáticamente con error 422 y el detalle.
"""
from typing import Literal, Optional
from datetime import date

from pydantic import BaseModel, Field

TipoSax = Literal["Soprano", "Alto", "Tenor", "Barítono"]
EstadoSax = Literal["Disponible", "Reservado", "En mantenimiento", "Vendido"]
EstadoMant = Literal["Pendiente", "En proceso", "Terminado"]


class MarcaIn(BaseModel):
    nombre: str = Field(min_length=1, max_length=60)
    pais: Optional[str] = Field(default=None, max_length=60)


class SaxofonIn(BaseModel):
    marca_id: int
    modelo: str = Field(min_length=1, max_length=80)
    tipo: TipoSax
    numero_serie: str = Field(min_length=1, max_length=40)
    acabado: Optional[str] = None
    anio: Optional[int] = Field(default=None, ge=1840, le=2100)  # el saxofón se inventó en 1840
    precio: float = Field(ge=0)
    estado: EstadoSax = "Disponible"


class ClienteIn(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    telefono: Optional[str] = Field(default=None, max_length=20)
    correo: Optional[str] = Field(default=None, max_length=100)


class MantenimientoIn(BaseModel):
    saxofon_id: int
    cliente_id: int
    fecha: date
    descripcion: str = Field(min_length=1, max_length=300)
    costo: float = Field(default=0, ge=0)
    estado: EstadoMant = "Pendiente"
