"""
API REST con FastAPI para el Sistema de Enrutamiento de Reclamos Bancarios.
Endpoints:
- POST /clasificar: clasifica un reclamo por area y prioridad
- POST /asignar: asigna de forma optima una lista de reclamos a areas
- GET /reclamos: lista reclamos registrados (en memoria)
- GET /info: informacion del sistema
"""

import os
import sys
from typing import List, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Agregar backend al path para importar modulos locales
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ml_model import clasificador
from optimizacion import OptimizadorEnrutamiento

app = FastAPI(
    title="Sistema de Enrutamiento de Reclamos Bancarios",
    description="Clasificacion y enrutamiento inteligente de reclamos de banca movil",
    version="1.0.0",
)

# CORS para permitir peticiones desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

optimizador = OptimizadorEnrutamiento()

# Almacenamiento en memoria (para MVP; en produccion usar BD)
reclamos_registrados = []


# -------------------- Modelos de datos (Pydantic) --------------------

class ReclamoEntrada(BaseModel):
    texto: str
    id: Optional[str] = None


class ClasificacionSalida(BaseModel):
    id: str
    texto: str
    area: str
    prioridad: str
    probabilidades_area: dict
    probabilidades_prioridad: dict


class ReclamoParaAsignar(BaseModel):
    id: str
    texto: str
    area_predicha: str
    prioridad: str
    probabilidad_area: float = 0.5


class AsignacionSalida(BaseModel):
    id: str
    texto: str
    area_asignada: str
    area_predicha: str
    prioridad: str
    probabilidad_confianza: float
    sla_horas: int


class AsignacionEntrada(BaseModel):
    reclamos: List[ReclamoParaAsignar]


# -------------------- Endpoints --------------------


@app.on_event("startup")
def startup_event():
    """Entrena o carga los modelos al iniciar la API."""
    modelo_path = os.path.join(os.path.dirname(__file__), "modelos", "vectorizer.pkl")
    if os.path.exists(modelo_path):
        clasificador.cargar_modelos()
        print("Modelos cargados desde disco.")
    else:
        print("Entrenando modelos por primera vez...")
        clasificador.entrenar()
        print("Modelos entrenados y guardados.")


@app.get("/info")
def info():
    return {
        "sistema": "Enrutamiento de Reclamos Bancarios",
        "version": "1.0.0",
        "areas": clasificador.obtener_areas_disponibles(),
        "prioridades": clasificador.obtener_prioridades_disponibles(),
        "capacidades": optimizador.obtener_capacidades(),
        "slas": optimizador.obtener_slas(),
    }


@app.post("/clasificar", response_model=ClasificacionSalida)
def clasificar(reclamo: ReclamoEntrada):
    """
    Clasifica un reclamo individual por area y prioridad usando el modelo ML.
    """
    if not reclamo.texto or not reclamo.texto.strip():
        raise HTTPException(status_code=400, detail="El texto del reclamo no puede estar vacío")

    resultado = clasificador.predecir(reclamo.texto)

    reclamo_id = reclamo.id or f"REC-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    registro = {
        "id": reclamo_id,
        "texto": reclamo.texto,
        "area": resultado["area"],
        "prioridad": resultado["prioridad"],
        "fecha": datetime.now().isoformat(),
        "probabilidades_area": resultado["probabilidades_area"],
        "probabilidades_prioridad": resultado["probabilidades_prioridad"],
    }
    reclamos_registrados.append(registro)

    return {
        "id": reclamo_id,
        "texto": reclamo.texto,
        "area": resultado["area"],
        "prioridad": resultado["prioridad"],
        "probabilidades_area": resultado["probabilidades_area"],
        "probabilidades_prioridad": resultado["probabilidades_prioridad"],
    }


@app.post("/asignar", response_model=List[AsignacionSalida])
def asignar(entrada: AsignacionEntrada):
    """
    Asigna una lista de reclamos a áreas de forma óptima usando optimización
    matemática (programación lineal entera).
    """
    if not entrada.reclamos:
        raise HTTPException(status_code=400, detail="La lista de reclamos no puede estar vacía")

    reclamos_dict = [r.model_dump() for r in entrada.reclamos]

    # Calcular carga actual por área (simulada)
    carga_actual = {}
    for area in optimizador.obtener_capacidades():
        carga_actual[area] = 0

    for r in reclamos_dict:
        r["carga_actual_area"] = carga_actual

    asignaciones = optimizador.asignar_optimo(reclamos_dict)

    if not asignaciones:
        raise HTTPException(status_code=500, detail="No se pudo realizar la asignación óptima")

    return asignaciones


@app.get("/reclamos")
def listar_reclamos():
    """Devuelve todos los reclamos clasificados hasta ahora."""
    return reclamos_registrados


@app.get("/reclamos/{reclamo_id}")
def obtener_reclamo(reclamo_id: str):
    for r in reclamos_registrados:
        if r["id"] == reclamo_id:
            return r
    raise HTTPException(status_code=404, detail="Reclamo no encontrado")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)