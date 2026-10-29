"""
SaxManager - Punto de entrada de FastAPI.

Ejecutar en local:
    uvicorn app.main:app --reload
Luego abrir http://127.0.0.1:8000  (frontend)
y      http://127.0.0.1:8000/docs (documentación automática de la API)
"""
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.database import crear_base_si_no_existe
from app.routers import clientes, mantenimientos, marcas, saxofones

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

app = FastAPI(
    title="SaxManager API",
    description="API para administrar el inventario y taller de una tienda de saxofones",
    version="1.0.0",
)

# Permite que el frontend llame a la API aunque se abra desde otro origen (ej. Live Server)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

crear_base_si_no_existe()

# Rutas de la API
app.include_router(marcas.router)
app.include_router(saxofones.router)
app.include_router(clientes.router)
app.include_router(mantenimientos.router)


# Frontend (HTML, CSS y JS)
app.mount("/css", StaticFiles(directory=FRONTEND_DIR / "css"), name="css")
app.mount("/js", StaticFiles(directory=FRONTEND_DIR / "js"), name="js")


@app.get("/", include_in_schema=False)
def inicio():
    return FileResponse(FRONTEND_DIR / "index.html")
