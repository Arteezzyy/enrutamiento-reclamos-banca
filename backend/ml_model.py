"""
Modulo de Machine Learning para clasificacion de reclamos bancarios.
Utiliza TF-IDF para extraccion de características y Regresion Logistica
para clasificacion supervisada (area + prioridad).
"""

import os
import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, f1_score, accuracy_score

# Rutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATOS_DIR = os.path.join(BASE_DIR, "datos")
MODELOS_DIR = os.path.join(BASE_DIR, "modelos")
CSV_PATH = os.path.join(DATOS_DIR, "reclamos.csv")

AREA_MODEL_PATH = os.path.join(MODELOS_DIR, "area_model.pkl")
PRIORIDAD_MODEL_PATH = os.path.join(MODELOS_DIR, "prioridad_model.pkl")
VECTORIZER_PATH = os.path.join(MODELOS_DIR, "vectorizer.pkl")
LE_AREA_PATH = os.path.join(MODELOS_DIR, "le_area.pkl")
LE_PRIORIDAD_PATH = os.path.join(MODELOS_DIR, "le_prioridad.pkl")

os.makedirs(MODELOS_DIR, exist_ok=True)


class ClasificadorReclamos:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=5000, stop_words=None, ngram_range=(1, 2))
        self.le_area = LabelEncoder()
        self.le_prioridad = LabelEncoder()
        self.model_area = LogisticRegression(max_iter=1000, random_state=42)
        self.model_prioridad = LogisticRegression(max_iter=1000, random_state=42)
        self.entrenado = False

    def cargar_datos(self, ruta_csv=CSV_PATH):
        """Carga el dataset de reclamos desde CSV."""
        df = pd.read_csv(ruta_csv)
        df = df.dropna(subset=["texto", "area", "prioridad"])
        return df

    def entrenar(self, ruta_csv=CSV_PATH):
        """Entrena los modelos de area y prioridad."""
        df = self.cargar_datos(ruta_csv)

        X = df["texto"].values
        y_area = df["area"].values
        y_prioridad = df["prioridad"].values

        # Vectorizar texto
        X_vec = self.vectorizer.fit_transform(X)

        # Codificar etiquetas
        y_area_enc = self.le_area.fit_transform(y_area)
        y_prioridad_enc = self.le_prioridad.fit_transform(y_prioridad)

        # División train/test para evaluación
        X_train, X_test, ya_train, ya_test, yp_train, yp_test = train_test_split(
            X_vec, y_area_enc, y_prioridad_enc, test_size=0.2, random_state=42
        )

        # Entrenar modelo de Área
        self.model_area.fit(X_train, ya_train)
        pred_area = self.model_area.predict(X_test)
        acc_area = accuracy_score(ya_test, pred_area)
        f1_area = f1_score(ya_test, pred_area, average="weighted")

        # Entrenar modelo de Prioridad
        self.model_prioridad.fit(X_train, yp_train)
        pred_prioridad = self.model_prioridad.predict(X_test)
        acc_pri = accuracy_score(yp_test, pred_prioridad)
        f1_pri = f1_score(yp_test, pred_prioridad, average="weighted")

        self.entrenado = True

        print("=== RESULTADOS DE ENTRENAMIENTO ===")
        print(f"Area - Accuracy: {acc_area:.4f} | F1-score: {f1_area:.4f}")
        print(f"Prioridad - Accuracy: {acc_pri:.4f} | F1-score: {f1_pri:.4f}")
        print("\nReporte Area:\n", classification_report(ya_test, pred_area, target_names=self.le_area.classes_))
        print("\nReporte Prioridad:\n", classification_report(yp_test, pred_prioridad, target_names=self.le_prioridad.classes_))

        # Guardar modelos
        self.guardar_modelos()

        return {
            "area": {"accuracy": acc_area, "f1_score": f1_area},
            "prioridad": {"accuracy": acc_pri, "f1_score": f1_pri},
        }

    def guardar_modelos(self):
        """Guarda los modelos entrenados en disco."""
        joblib.dump(self.vectorizer, VECTORIZER_PATH)
        joblib.dump(self.model_area, AREA_MODEL_PATH)
        joblib.dump(self.model_prioridad, PRIORIDAD_MODEL_PATH)
        joblib.dump(self.le_area, LE_AREA_PATH)
        joblib.dump(self.le_prioridad, LE_PRIORIDAD_PATH)

    def cargar_modelos(self):
        """Carga modelos previamente guardados."""
        self.vectorizer = joblib.load(VECTORIZER_PATH)
        self.model_area = joblib.load(AREA_MODEL_PATH)
        self.model_prioridad = joblib.load(PRIORIDAD_MODEL_PATH)
        self.le_area = joblib.load(LE_AREA_PATH)
        self.le_prioridad = joblib.load(LE_PRIORIDAD_PATH)
        self.entrenado = True

    def predecir(self, texto):
        """
        Predice area y prioridad para un texto dado.
        Retorna diccionario con area, prioridad y probabilidades.
        """
        if not self.entrenado:
            self.cargar_modelos()

        X_vec = self.vectorizer.transform([texto])

        area_enc = self.model_area.predict(X_vec)[0]
        prioridad_enc = self.model_prioridad.predict(X_vec)[0]

        area = self.le_area.inverse_transform([area_enc])[0]
        prioridad = self.le_prioridad.inverse_transform([prioridad_enc])[0]

        # Probabilidades
        proba_area = self.model_area.predict_proba(X_vec)[0]
        proba_prioridad = self.model_prioridad.predict_proba(X_vec)[0]

        area_probs = dict(zip(self.le_area.classes_, proba_area.tolist()))
        prioridad_probs = dict(zip(self.le_prioridad.classes_, proba_prioridad.tolist()))

        return {
            "area": area,
            "prioridad": prioridad,
            "probabilidades_area": area_probs,
            "probabilidades_prioridad": prioridad_probs,
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