"""
Modulo de Machine Learning para clasificacion de reclamos bancarios.

Pipeline:
    texto -> normalizacion PLN -> TF-IDF -> Regresion Logistica

Se entrenan dos clasificadores supervisados (area de destino y prioridad) y
se guardan en disco para evitar reentrenar en cada ejecucion.
"""

import os
import re
import unicodedata

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import GridSearchCV, StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder

# Rutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATOS_DIR = os.path.join(BASE_DIR, "datos")
MODELOS_DIR = os.path.join(BASE_DIR, "modelos")
CSV_PATH = os.path.join(DATOS_DIR, "reclamos.csv")
METRICAS_PATH = os.path.join(BASE_DIR, "metricas.json")

AREA_MODEL_PATH = os.path.join(MODELOS_DIR, "area_model.pkl")
PRIORIDAD_MODEL_PATH = os.path.join(MODELOS_DIR, "prioridad_model.pkl")
VECTORIZER_PATH = os.path.join(MODELOS_DIR, "vectorizer.pkl")
VECTORIZER_PRIORIDAD_PATH = os.path.join(MODELOS_DIR, "vectorizer_prioridad.pkl")
LE_AREA_PATH = os.path.join(MODELOS_DIR, "le_area.pkl")
LE_PRIORIDAD_PATH = os.path.join(MODELOS_DIR, "le_prioridad.pkl")

os.makedirs(MODELOS_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Preprocesamiento de texto (PLN)
# ---------------------------------------------------------------------------

_CARACTERES_NO_VALIDOS = re.compile(r"[^a-z0-9\s]")
_ESPACIOS = re.compile(r"\s+")


def normalizar_texto(texto):
    """
    Normaliza un reclamo: minusculas, sin tildes, sin signos y con espacios
    simples. Se aplica tanto al entrenamiento como a la prediccion para evitar
    diferencias entre ambos caminos.
    """
    if texto is None:
        return ""
    texto = str(texto).lower().strip()
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(caracter for caracter in texto if unicodedata.category(caracter) != "Mn")
    texto = _CARACTERES_NO_VALIDOS.sub(" ", texto)
    return _ESPACIOS.sub(" ", texto).strip()


def normalizar_corpus(textos):
    return [normalizar_texto(texto) for texto in textos]


def _parametros_vectorizador(params=None):
    base = {
        "max_features": 5000,
        "stop_words": None,
        "ngram_range": (1, 2),
        "min_df": 1,
    }
    base.update(params or {})
    return base


def _parametros_modelo(params=None):
    base = {
        "max_iter": 2000,
        "random_state": 42,
        "class_weight": "balanced",
    }
    base.update(params or {})
    return base


def construir_pipeline(tfidf_params=None, model_params=None):
    """Pipeline de sklearn usado para validacion cruzada y busqueda de hiperparametros."""
    vectorizador = TfidfVectorizer(**_parametros_vectorizador(tfidf_params))
    modelo = LogisticRegression(**_parametros_modelo(model_params))
    return Pipeline([("tfidf", vectorizador), ("modelo", modelo)])


def _a_python(valor):
    """Convierte tipos de numpy a tipos nativos para poder serializar a JSON."""
    if isinstance(valor, dict):
        return {str(clave): _a_python(contenido) for clave, contenido in valor.items()}
    if isinstance(valor, (list, tuple)):
        return [_a_python(contenido) for contenido in valor]
    if hasattr(valor, "item"):
        return valor.item()
    return valor


class ClasificadorReclamos:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(**_parametros_vectorizador())
        self.vectorizer_prioridad = TfidfVectorizer(**_parametros_vectorizador())
        self.le_area = LabelEncoder()
        self.le_prioridad = LabelEncoder()
        self.model_area = LogisticRegression(**_parametros_modelo())
        self.model_prioridad = LogisticRegression(**_parametros_modelo())
        self.entrenado = False
        self.metricas_entrenamiento = None

    # ------------------------------------------------------------------
    # Datos
    # ------------------------------------------------------------------

    def cargar_datos(self, ruta_csv=CSV_PATH):
        df = pd.read_csv(ruta_csv)
        df = df.dropna(subset=["texto", "area", "prioridad"])
        return df

    # ------------------------------------------------------------------
    # Entrenamiento y evaluacion
    # ------------------------------------------------------------------

    def optimizar_hiperparametros(self, df=None, cv=5):
        """
        Busca los mejores hiperparametros de TF-IDF + Regresion Logistica
        mediante GridSearchCV con validacion cruzada estratificada.
        """
        df = self.cargar_datos() if df is None else df
        X = normalizar_corpus(df["texto"])

        grilla = {
            "tfidf__ngram_range": [(1, 1), (1, 2)],
            "tfidf__min_df": [1, 2],
            "modelo__C": [0.5, 1.0, 2.0, 5.0],
        }
        validacion = StratifiedKFold(n_splits=cv, shuffle=True, random_state=42)

        resultados = {}
        for objetivo in ("area", "prioridad"):
            y = df[objetivo].values
            busqueda = GridSearchCV(
                construir_pipeline(),
                grilla,
                cv=validacion,
                scoring="f1_macro",
                n_jobs=1,
            )
            busqueda.fit(X, y)

            mejores = busqueda.best_params_
            resultados[objetivo] = {
                "tfidf_params": {
                    "ngram_range": mejores["tfidf__ngram_range"],
                    "min_df": mejores["tfidf__min_df"],
                },
                "modelo_params": {"C": mejores["modelo__C"]},
                "f1_macro_cv": float(busqueda.best_score_),
            }

        return resultados

    def evaluar_cv(self, df=None, tfidf_params=None, model_params=None, cv=5):
        """Metricas de validacion cruzada estratificada (sin fuga de datos)."""
        df = self.cargar_datos() if df is None else df
        X = normalizar_corpus(df["texto"])
        validacion = StratifiedKFold(n_splits=cv, shuffle=True, random_state=42)

        puntajes = {
            "accuracy": "accuracy",
            "precision_macro": "precision_macro",
            "recall_macro": "recall_macro",
            "f1_macro": "f1_macro",
            "f1_weighted": "f1_weighted",
        }

        resultados = {}
        for objetivo in ("area", "prioridad"):
            y = df[objetivo].values
            pipeline = construir_pipeline(tfidf_params, model_params)
            metricas_objetivo = {}
            for nombre_metrica, scoring in puntajes.items():
                puntuaciones = cross_val_score(
                    pipeline, X, y, cv=validacion, scoring=scoring, n_jobs=1
                )
                metricas_objetivo[nombre_metrica] = {
                    "media": float(puntuaciones.mean()),
                    "std": float(puntuaciones.std()),
                }
            resultados[objetivo] = metricas_objetivo

        return resultados

    def evaluar_holdout(
        self,
        df=None,
        tfidf_params=None,
        model_params=None,
        test_size=0.2,
        random_state=42,
    ):
        """Metricas sobre una particion estratificada de prueba (20 % por defecto)."""
        df = self.cargar_datos() if df is None else df
        X = normalizar_corpus(df["texto"])

        resultados = {}
        for objetivo in ("area", "prioridad"):
            y = df[objetivo].values
            X_train, X_test, y_train, y_test = train_test_split(
                X,
                y,
                test_size=test_size,
                random_state=random_state,
                stratify=y,
            )

            vectorizador = TfidfVectorizer(**_parametros_vectorizador(tfidf_params))
            X_train_vec = vectorizador.fit_transform(X_train)
            X_test_vec = vectorizador.transform(X_test)

            modelo = LogisticRegression(**_parametros_modelo(model_params))
            modelo.fit(X_train_vec, y_train)
            predicciones = modelo.predict(X_test_vec)

            resultados[objetivo] = _a_python(
                {
                    "muestra": int(len(y_test)),
                    "accuracy": accuracy_score(y_test, predicciones),
                    "precision_macro": precision_score(
                        y_test, predicciones, average="macro", zero_division=0
                    ),
                    "recall_macro": recall_score(
                        y_test, predicciones, average="macro", zero_division=0
                    ),
                    "f1_macro": f1_score(y_test, predicciones, average="macro", zero_division=0),
                    "f1_weighted": f1_score(
                        y_test, predicciones, average="weighted", zero_division=0
                    ),
                    "reporte": classification_report(
                        y_test, predicciones, output_dict=True, zero_division=0
                    ),
                }
            )

        return resultados

    def entrenar(
        self,
        ruta_csv=CSV_PATH,
        params_area=None,
        params_prioridad=None,
        evaluar=True,
        verbose=True,
    ):
        """
        Entrena los dos clasificadores con el corpus completo y guarda los
        artefactos en disco. Cada tarea puede usar sus propios hiperparametros.
        """
        df = self.cargar_datos(ruta_csv)
        X = normalizar_corpus(df["texto"])
        y_area = df["area"].values
        y_prioridad = df["prioridad"].values

        params_area = params_area or {}
        params_prioridad = params_prioridad or {}

        self.vectorizer = TfidfVectorizer(
            **_parametros_vectorizador(params_area.get("tfidf_params"))
        )
        X_area = self.vectorizer.fit_transform(X)

        self.vectorizer_prioridad = TfidfVectorizer(
            **_parametros_vectorizador(
                params_prioridad.get("tfidf_params") or params_area.get("tfidf_params")
            )
        )
        X_prioridad = self.vectorizer_prioridad.fit_transform(X)

        self.le_area = LabelEncoder()
        self.le_prioridad = LabelEncoder()
        y_area_enc = self.le_area.fit_transform(y_area)
        y_prioridad_enc = self.le_prioridad.fit_transform(y_prioridad)

        self.model_area = LogisticRegression(
            **_parametros_modelo(params_area.get("modelo_params"))
        )
        self.model_area.fit(X_area, y_area_enc)

        self.model_prioridad = LogisticRegression(
            **_parametros_modelo(params_prioridad.get("modelo_params"))
        )
        self.model_prioridad.fit(X_prioridad, y_prioridad_enc)

        self.entrenado = True
        self.guardar_modelos()

        if evaluar:
            metricas_area = self.evaluar_holdout(
                df,
                tfidf_params=params_area.get("tfidf_params"),
                model_params=params_area.get("modelo_params"),
            )
            metricas_prioridad = self.evaluar_holdout(
                df,
                tfidf_params=params_prioridad.get("tfidf_params")
                or params_area.get("tfidf_params"),
                model_params=params_prioridad.get("modelo_params")
                or params_area.get("modelo_params"),
            )
            self.metricas_entrenamiento = {
                "area": metricas_area["area"],
                "prioridad": metricas_prioridad["prioridad"],
            }
            if verbose:
                for objetivo in ("area", "prioridad"):
                    metricas = self.metricas_entrenamiento[objetivo]
                    print(
                        f"{objetivo.capitalize()} - Accuracy: {metricas['accuracy']:.4f} | "
                        f"F1 ponderado: {metricas['f1_weighted']:.4f} | "
                        f"F1 macro: {metricas['f1_macro']:.4f}"
                    )

        return self.metricas_entrenamiento

    # ------------------------------------------------------------------
    # Persistencia
    # ------------------------------------------------------------------

    def guardar_modelos(self):
        joblib.dump(self.vectorizer, VECTORIZER_PATH)
        joblib.dump(self.vectorizer_prioridad, VECTORIZER_PRIORIDAD_PATH)
        joblib.dump(self.model_area, AREA_MODEL_PATH)
        joblib.dump(self.model_prioridad, PRIORIDAD_MODEL_PATH)
        joblib.dump(self.le_area, LE_AREA_PATH)
        joblib.dump(self.le_prioridad, LE_PRIORIDAD_PATH)

    def cargar_modelos(self):
        self.vectorizer = joblib.load(VECTORIZER_PATH)
        if os.path.exists(VECTORIZER_PRIORIDAD_PATH):
            self.vectorizer_prioridad = joblib.load(VECTORIZER_PRIORIDAD_PATH)
        else:
            self.vectorizer_prioridad = self.vectorizer
        self.model_area = joblib.load(AREA_MODEL_PATH)
        self.model_prioridad = joblib.load(PRIORIDAD_MODEL_PATH)
        self.le_area = joblib.load(LE_AREA_PATH)
        self.le_prioridad = joblib.load(LE_PRIORIDAD_PATH)
        self.entrenado = True

    # ------------------------------------------------------------------
    # Prediccion
    # ------------------------------------------------------------------

    def predecir(self, texto):
        """Predice area y prioridad para un texto y devuelve sus probabilidades."""
        if not self.entrenado:
            self.cargar_modelos()

        texto_normalizado = normalizar_texto(texto)
        X_area = self.vectorizer.transform([texto_normalizado])
        X_prioridad = self.vectorizer_prioridad.transform([texto_normalizado])

        area_enc = self.model_area.predict(X_area)[0]
        prioridad_enc = self.model_prioridad.predict(X_prioridad)[0]

        area = self.le_area.inverse_transform([area_enc])[0]
        prioridad = self.le_prioridad.inverse_transform([prioridad_enc])[0]

        proba_area = self.model_area.predict_proba(X_area)[0]
        proba_prioridad = self.model_prioridad.predict_proba(X_prioridad)[0]

        return {
            "area": area,
            "prioridad": prioridad,
            "probabilidades_area": dict(zip(self.le_area.classes_, proba_area.tolist())),
            "probabilidades_prioridad": dict(
                zip(self.le_prioridad.classes_, proba_prioridad.tolist())
            ),
        }

    def obtener_areas_disponibles(self):
        if not self.entrenado:
            self.cargar_modelos()
        return self.le_area.classes_.tolist()

    def obtener_prioridades_disponibles(self):
        if not self.entrenado:
            self.cargar_modelos()
        return self.le_prioridad.classes_.tolist()


# Instancia singleton para usar en la API
clasificador = ClasificadorReclamos()
