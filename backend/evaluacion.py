"""
Evaluacion de impacto del sistema de enrutamiento (objetivo II.2.4).

Simula el "First Routing Time" (tiempo medio de reenvio/derivacion) comparando:

1. PROCESO MANUAL (baseline): un operador lee cada reclamo y lo deriva al area
   correcta. El tiempo depende de la prioridad (mas urgente = mas lento por la
   gravedad del caso) y de la familiaridad del operador con cada area.
2. PROCESO AUTOMATIZADO: el modelo ML clasifica instantaneamente y la optimizacion
   asigna el area en milisegundos. El tiempo es casi constante.

Output:
- reporte por consola
- backend/evaluacion_impacto.json con los resultados
"""

import json
import os
import random
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Supuestos de negocio (horas-hombre para derivar un reclamo manualmente).
# Se asumen como estimaciones operativas del area de atencion al cliente.
TIEMPO_MANUAL_POR_PRIORIDAD = {
    "Alta": 1.5,   # casos complejos, requieren revision de documentos
    "Media": 0.8,
    "Baja": 0.3,   # consultas simples, derivacion rapida
}

# Penalizacion por error de derivacion manual (el reclamo vuelve y se re-derecha).
PROB_ERROR_MANUAL = 0.12
TIEMPO_REDERIVACION = 1.0  # horas extra por cada reclamo mal derivado

# Tiempo fijo del proceso automatizado (clasificacion + optimizacion ILP).
TIEMPO_AUTO_POR_RECLAMO_HORAS = 0.002  # ~7 segundos por reclamo


def simular_proceso_manual(reclamos, semilla=42):
    random.seed(semilla)
    total_horas = 0.0
    detalle = []

    for r in reclamos:
        prioridad = r["prioridad"]
        base = TIEMPO_MANUAL_POR_PRIORIDAD.get(prioridad, 0.8)

        # Variabilidad del operador (+/- 25 %)
        variacion = random.uniform(0.75, 1.25)
        tiempo = base * variacion

        # Posible error de derivacion que obliga a re-derivar
        error = random.random() < PROB_ERROR_MANUAL
        if error:
            tiempo += TIEMPO_REDERIVACION

        total_horas += tiempo
        detalle.append(
            {
                "id": r["id"],
                "prioridad": prioridad,
                "tiempo_manual_horas": round(tiempo, 4),
                "error_derivacion": error,
            }
        )

    return {
        "total_horas": round(total_horas, 4),
        "tiempo_promedio_por_reclamo_horas": round(total_horas / len(reclamos), 6),
        "detalle": detalle,
    }


def simular_proceso_automatizado(reclamos):
    total_horas = TIEMPO_AUTO_POR_RECLAMO_HORAS * len(reclamos)
    return {
        "total_horas": round(total_horas, 6),
        "tiempo_promedio_por_reclamo_horas": round(
            TIEMPO_AUTO_POR_RECLAMO_HORAS, 6
        ),
    }


def main():
    print("=" * 74)
    print("EVALUACION DE IMPACTO - FIRST ROUTING TIME")
    print("=" * 74)

    # Cargar reclamos historicos como muestra de evaluacion.
    datos_path = os.path.join(BASE_DIR, "datos", "reclamos.csv")
    try:
        import pandas as pd

        df = pd.read_csv(datos_path)
        reclamos = [
            {
                "id": f"REC-{i:03d}",
                "texto": row["texto"],
                "area": row["area"],
                "prioridad": row["prioridad"],
            }
            for i, (_, row) in enumerate(df.iterrows(), start=1)
        ]
    except Exception as exc:
        print(f"No se pudo cargar el dataset para evaluar: {exc}")
        return

    print(f"Reclamos evaluados: {len(reclamos)}")

    manual = simular_proceso_manual(reclamos)
    automatico = simular_proceso_automatizado(reclamos)

    ahorro_horas = manual["total_horas"] - automatico["total_horas"]
    porcentaje_ahorro = (
        (ahorro_horas / manual["total_horas"]) * 100 if manual["total_horas"] else 0
    )
    aceleracion = (
        manual["tiempo_promedio_por_reclamo_horas"]
        / automatico["tiempo_promedio_por_reclamo_horas"]
    )

    print(f"\nProceso manual (baseline):")
    print(f"  Tiempo total:          {manual['total_horas']:.2f} horas-hombre")
    print(f"  Promedio/reclamo:      {manual['tiempo_promedio_por_reclamo_horas']:.4f} horas")
    print(f"  Errores de derivacion: {sum(1 for d in manual['detalle'] if d['error_derivacion'])}")

    print(f"\nProceso automatizado (sistema propuesto):")
    print(f"  Tiempo total:          {automatico['total_horas']:.4f} horas-hombre")
    print(f"  Promedio/reclamo:      {automatico['tiempo_promedio_por_reclamo_horas']:.6f} horas")

    print(f"\nImpacto:")
    print(f"  Ahorro de tiempo:      {ahorro_horas:.2f} horas-hombre ({porcentaje_ahorro:.1f} %)")
    print(f"  Aceleracion:           {aceleracion:.0f}x mas rapido por reclamo")

    reporte = {
        "generado": datetime.now().isoformat(timespec="seconds"),
        "reclamos_evaluados": len(reclamos),
        "proceso_manual": manual,
        "proceso_automatizado": automatico,
        "impacto": {
            "ahorro_horas": round(ahorro_horas, 4),
            "porcentaje_ahorro": round(porcentaje_ahorro, 2),
            "aceleracion_veces": round(aceleracion, 2),
        },
        "supuestos": {
            "tiempo_manual_por_prioridad": TIEMPO_MANUAL_POR_PRIORIDAD,
            "prob_error_manual": PROB_ERROR_MANUAL,
            "tiempo_auto_por_reclamo_horas": TIEMPO_AUTO_POR_RECLAMO_HORAS,
        },
    }

    salida_path = os.path.join(BASE_DIR, "evaluacion_impacto.json")
    with open(salida_path, "w", encoding="utf-8") as archivo:
        json.dump(reporte, archivo, ensure_ascii=False, indent=2)

    print(f"\nReporte guardado en {salida_path}")


if __name__ == "__main__":
    main()
