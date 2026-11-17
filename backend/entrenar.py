"""
Script de entrenamiento y evaluacion del modelo de clasificacion.

Uso:
    python entrenar.py

Pasos:
1. Carga y describe el dataset.
2. Busca hiperparametros (GridSearchCV) para area y prioridad.
3. Evalua con validacion cruzada estratificada de 5 pliegues.
4. Evalua sobre una particion de prueba (20 %).
5. Entrena el modelo final con todo el corpus y guarda los artefactos.
6. Escribe `metricas.json` con los resultados.
"""

import json
import os
from datetime import datetime

import pandas as pd

from ml_model import METRICAS_PATH, _a_python, clasificador


def describir_dataset(df):
    areas = df["area"].value_counts().to_dict()
    prioridades = df["prioridad"].value_counts().to_dict()
    matriz = {}
    for area in areas:
        matriz[area] = (
            df[df["area"] == area]["prioridad"].value_counts().to_dict()
        )
    return {
        "total": int(len(df)),
        "areas": {str(k): int(v) for k, v in areas.items()},
        "prioridades": {str(k): int(v) for k, v in prioridades.items()},
        "matriz_area_prioridad": matriz,
        "duplicados": int(df["texto"].duplicated().sum()),
        "longitud_media_texto": round(float(df["texto"].str.len().mean()), 2),
    }


def main():
    print("=" * 74)
    print("ENTRENAMIENTO Y EVALUACION - ENRUTAMIENTO DE RECLAMOS BANCARIOS")
    print("=" * 74)

    df = clasificador.cargar_datos()
    dataset = describir_dataset(df)

    print(f"\nDataset: {dataset['total']} reclamos")
    print(f"  Areas:       {dataset['areas']}")
    print(f"  Prioridades: {dataset['prioridades']}")
    print(f"  Duplicados:  {dataset['duplicados']}")

    print("\n[1/4] Busqueda de hiperparametros (GridSearchCV, 5-fold, f1_macro)...")
    mejoras = clasificador.optimizar_hiperparametros(df)
    for objetivo, informacion in mejoras.items():
        print(
            f"  {objetivo:10s} -> tfidf={informacion['tfidf_params']} "
            f"modelo={informacion['modelo_params']} "
            f"(f1_macro_cv={informacion['f1_macro_cv']:.4f})"
        )

    print("\n[2/4] Validacion cruzada estratificada (5 pliegues)...")
    metricas_cv = clasificador.evaluar_cv(
        df,
        tfidf_params=mejoras["area"]["tfidf_params"],
        model_params=mejoras["area"]["modelo_params"],
    )
    for objetivo in ("area", "prioridad"):
        cv = metricas_cv[objetivo]
        print(
            f"  {objetivo:10s} accuracy={cv['accuracy']['media']:.4f} "
            f"(+/- {cv['accuracy']['std']:.4f}) | "
            f"f1_macro={cv['f1_macro']['media']:.4f} | "
            f"f1_weighted={cv['f1_weighted']['media']:.4f}"
        )

    print("\n[3/4] Particion de prueba estratificada (20 %)...")
    metricas_holdout = {}
    for objetivo in ("area", "prioridad"):
        holdout_completo = clasificador.evaluar_holdout(
            df,
            tfidf_params=mejoras[objetivo]["tfidf_params"],
            model_params=mejoras[objetivo]["modelo_params"],
        )
        metricas_holdout[objetivo] = holdout_completo[objetivo]
        holdout = metricas_holdout[objetivo]
        print(
            f"  {objetivo:10s} accuracy={holdout['accuracy']:.4f} | "
            f"f1_macro={holdout['f1_macro']:.4f} | "
            f"f1_weighted={holdout['f1_weighted']:.4f}"
        )

    print("\n[4/4] Entrenando modelo final con el 100 % del corpus...")
    clasificador.entrenar(
        params_area={
            "tfidf_params": mejoras["area"]["tfidf_params"],
            "modelo_params": mejoras["area"]["modelo_params"],
        },
        params_prioridad={
            "tfidf_params": mejoras["prioridad"]["tfidf_params"],
            "modelo_params": mejoras["prioridad"]["modelo_params"],
        },
        evaluar=False,
        verbose=False,
    )
    print("  Modelos guardados en backend/modelos/")

    metricas = {
        "generado": datetime.now().isoformat(timespec="seconds"),
        "dataset": dataset,
        "modelo": {},
    }
    for objetivo in ("area", "prioridad"):
        metricas["modelo"][objetivo] = {
            "tfidf_params": mejoras[objetivo]["tfidf_params"],
            "modelo_params": mejoras[objetivo]["modelo_params"],
            "busqueda": {"mejor_f1_macro_cv": mejoras[objetivo]["f1_macro_cv"]},
            "cv": metricas_cv[objetivo],
            "holdout": metricas_holdout[objetivo],
        }

    # Conservar una evaluacion de impacto previa si ya existe.
    if os.path.exists(METRICAS_PATH):
        try:
            with open(METRICAS_PATH, "r", encoding="utf-8") as archivo:
                anteriores = json.load(archivo)
            if "impacto" in anteriores:
                metricas["impacto"] = anteriores["impacto"]
        except (json.JSONDecodeError, OSError):
            pass

    with open(METRICAS_PATH, "w", encoding="utf-8") as archivo:
        json.dump(_a_python(metricas), archivo, ensure_ascii=False, indent=2)

    print(f"\nMetricas guardadas en {METRICAS_PATH}")
    print("Siguiente paso: python evaluacion.py")


if __name__ == "__main__":
    main()
