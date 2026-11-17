"""
API REST con FastAPI para el Sistema de Enrutamiento de Reclamos Bancarios.

Endpoints:
- POST /clasificar: clasifica un reclamo por area y prioridad
- POST /asignar: asigna de forma optima una lista de reclamos a areas
- GET /reclamos: lista reclamos registrados (persistidos en SQLite)
- GET /info: informacion del sistema
- GET /metrica: metricas de entrenamiento/validacion del modelo
"""

import os
import sys
import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Agregar backend al path para importar modulos locales
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import json

from db import inicializar, insertar as db_insertar, listar as db_listar, contar as db_contar
from ml_model import clasificador
from optimizacion import (
    ErrorOptimizacion,
    OptimizadorEnrutamiento,
    OptimizacionInfactibleError,
    CapacidadInsuficienteError,
)

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

# Almacenamiento persistente en SQLite (reemplaza la lista en memoria)
inicializar()


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
    probabilidad_predicha: float
    sla_horas: int
    costo_asignacion: float


class AsignacionEntrada(BaseModel):
    reclamos: List[ReclamoParaAsignar]


# -------------------- Endpoints --------------------


@app.on_event("startup")
def startup_event():
    """Entrena o carga los modelos al iniciar la API."""
    modelo_path = os.path.join(os.path.dirname(__file__), "modelos", "area_model.pkl")
    if os.path.exists(modelo_path):
        clasificador.cargar_modelos()
        print("Modelos cargados desde disco.")
    else:
        print("Entrenando modelos por primera vez...")
        clasificador.entrenar()
        print("Modelos entrenados y guardados.")


@app.get("/health")
def health():
    """Endpoint de salud para saber si la API está corriendo."""
    return {
        "status": "ok",
        "sistema": "Enrutamiento de Reclamos Bancarios",
        "version": "1.0.0"
    }


@app.get("/info")
def info():
    return {
        "sistema": "Enrutamiento de Reclamos Bancarios",
        "version": "1.0.0",
        "areas": clasificador.obtener_areas_disponibles(),
        "prioridades": clasificador.obtener_prioridades_disponibles(),
        "capacidades": optimizador.obtener_capacidades(),
        "slas": optimizador.obtener_slas(),
        "parametros_optimizacion": optimizador.obtener_parametros(),
    }


@app.get("/metrica")
def metrica():
    """Devuelve las metricas de entrenamiento y validacion si existen."""
    metrica_path = os.path.join(os.path.dirname(__file__), "metricas.json")
    if not os.path.exists(metrica_path):
        raise HTTPException(status_code=404, detail="No hay metricas disponibles. Ejecuta backend/entrenar.py")
    with open(metrica_path, "r", encoding="utf-8") as archivo:
        return json.load(archivo)


@app.post("/clasificar", response_model=ClasificacionSalida)
def clasificar(reclamo: ReclamoEntrada):
    """
    Clasifica un reclamo individual por area y prioridad usando el modelo ML.
    """
    if not reclamo.texto or not reclamo.texto.strip():
        raise HTTPException(status_code=400, detail="El texto del reclamo no puede estar vacio")

    resultado = clasificador.predecir(reclamo.texto)

    reclamo_id = reclamo.id or f"REC-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6]}"
    registro = {
        "id": reclamo_id,
        "texto": reclamo.texto,
        "area": resultado["area"],
        "prioridad": resultado["prioridad"],
        "fecha": datetime.now().isoformat(),
        "probabilidades_area": resultado["probabilidades_area"],
        "probabilidades_prioridad": resultado["probabilidades_prioridad"],
    }

    try:
        db_insertar(registro)
    except Exception as exc:  # pragma: no cover - fallo de persistencia
        print(f"Advertencia: no se pudo persistir el reclamo {reclamo_id}: {exc}")

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
    Asigna una lista de reclamos a areas de forma optima usando optimización
    matematica (programacion lineal entera con CBC).
    """
    if not entrada.reclamos:
        raise HTTPException(status_code=400, detail="La lista de reclamos no puede estar vacia")

    reclamos_dict = [r.model_dump() for r in entrada.reclamos]

    try:
        resumen = optimizador.resolver(reclamos_dict, carga_actual={area: 0 for area in optimizador.obtener_capacidades()})
    except CapacidadInsuficienteError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        )
    except OptimizacionInfactibleError as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )

    if resumen["estado"] != "optimo":
        raise HTTPException(
            status_code=500,
            detail=f"El solver no pudo encontrar una solucion optima (estado: {resumen['estado']})",
        )

    return resumen["asignaciones"]


@app.get("/reclamos")
def listar_reclamos():
    """Devuelve todos los reclamos clasificados hasta ahora."""
    return db_listar()


@app.get("/reclamos/{reclamo_id}")
def obtener_reclamo(reclamo_id: str):
    registro = db_listar()  # TODO: optimizar con consulta por id cuando el volumen crezca
    for r in registro:
        if r["id"] == reclamo_id:
            return r
    raise HTTPException(status_code=404, detail="Reclamo no encontrado")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
