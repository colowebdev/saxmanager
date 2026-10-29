# Punto de entrada para Vercel: reutiliza la app de FastAPI
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.main import app  # noqa: E402,F401
