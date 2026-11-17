# 🏦 Sistema de Enrutamiento Inteligente de Reclamos Bancarios

Sistema de clasificación y enrutamiento automático de reclamos de banca móvil basado en **aprendizaje supervisado** y **optimización matemática**. Desarrollado como trabajo de la materia de Inteligencia Artificial — 1° Avance.

---

## 👥 Integrantes

| # | Nombre |
|---|--------|
| 1 | Valverde Soliz Dylan Andy |
| 2 | Alcoba Rodríguez Walter Sergio |
| 3 | Acuña Mariscal Gustavo |
| 4 | Ayaviri Quispe Yuri Daniel |
| 5 | David Martinez Antezana |
| 6 | Quispe Espinoza Juan Pablo |
| 7 | Lucas Mamani Villarroel |

- **Carrera:** Ingeniería de Sistemas  
- **Docente:** Erika Patricia Rodríguez Bilbao  
- **Universidad:** Universidad Mayor de San Simón (UMSS)  
- **Cochabamba – Bolivia**

---

## 🎯 Objetivo

Desarrollar un sistema supervisado de enrutamiento inteligente que procese automáticamente los reclamos de la banca móvil, clasificándolos simultáneamente por:

1. **Área de destino:** Soporte Técnico, Gerencia de Operaciones/Riesgo, Atención al Cliente
2. **Nivel de prioridad:** Alta, Media, Baja

Con el fin de reducir el tiempo de redistribución manual y optimizar la atención operativa.

---

## 📊 Dataset de Entrenamiento

- **Cantidad:** 150 reclamos sintéticos en español
- **Fuente:** Generados sintéticamente con escenarios realistas de banca móvil
- **Etiquetas:** Cada reclamo tiene asignada su área correcta y su nivel de prioridad
- **Distribución de áreas:**
  - Soporte Técnico
  - Gerencia de Operaciones/Riesgo
  - Atención al Cliente
- **Distribución de prioridades:**
  - Alta
  - Media
  - Baja
- **Archivo:** `backend/datos/reclamos.csv`

Ejemplos de reclamos incluidos:
- *"No puedo acceder a la aplicación móvil, se cierra cada vez que intento iniciar sesión"* → Soporte Técnico / Alta
- *"Hice una transferencia pero el dinero no llegó a la cuenta del destinatario"* → Gerencia de Operaciones/Riesgo / Alta
- *"Quisiera saber el horario de atención de la sucursal"* → Atención al Cliente / Baja

---

## 🧠 Modelo de Machine Learning

### Arquitectura

El sistema utiliza un modelo de **aprendizaje supervisado** con dos tareas de clasificación independientes:

| Tarea | Algoritmo | Entrada | Salida |
|-------|-----------|---------|--------|
| Clasificación de Área | Regresión Logística | Vector TF-IDF del texto | Área de destino |
| Clasificación de Prioridad | Regresión Logística | Vector TF-IDF del texto | Nivel de prioridad |

### Preprocesamiento de texto (PLN)

- **Vectorización:** TF-IDF (Term Frequency-Inverse Document Frequency)
- **N-gramas:** Unigramas y bigramas (`ngram_range=(1,2)`)
- **Máximo de características:** 5,000 términos más relevantes
- **Limpieza:** El texto se pasa tal como se recibe al vectorizador (sin stop-words en español para conservar palabras clave de contexto bancario)

### Entrenamiento

- División del dataset: 80% entrenamiento, 20% prueba
- Validación cruzada implícita mediante separación train/test
- Codificación de etiquetas con `LabelEncoder` de scikit-learn

### Métricas de evaluación

Al iniciar el sistema, se imprimen en consola los resultados:

- **Accuracy (Exactitud):** Proporción de predicciones correctas
- **F1-score (ponderado):** Media armónica entre precisión y sensibilidad, ponderada por el soporte de cada clase
- **Reporte de clasificación:** Precisión, recall y F1-score por cada clase (área y prioridad)

Los modelos se guardan automáticamente en `backend/modelos/` como archivos `.pkl` para no volver a entrenar en cada ejecución.

---

## ⚙️ Optimización Matemática (Asignación de Áreas)

Una vez que el modelo ML predice el área y prioridad de un reclamo, un segundo módulo de optimización asigna de forma óptima cada reclamo a un área operativa.

### Algoritmo

- **Programación Lineal Entera (ILP)** implementada con la librería **PuLP** (Python)
- Solver: CBC (incluido en PuLP)

### Función objetivo

Minimizar el costo total de asignación:

```
Costo_total = Σ [ Costo_base(área) × (1 − 0.5 × coincidencia_ML)
              + Penalización_SLA(prioridad) × (1 − confianza_modelo) ]
```

Donde:
- **Coincidencia ML:** 1 si el área asignada coincide con la predicción del modelo, 0 en caso contrario
- **Confianza del modelo:** Probabilidad emitida por el clasificador (0 a 1)
- **Penalización SLA:** Mayor para prioridad Alta, menor para Baja

### Restricciones

1. **Cada reclamo se asigna a exactamente un área** (restricción de asignación única)
2. **Capacidad máxima por área:** No se excede el número máximo de reclamos que cada área puede atender por turno

### Parámetros de negocio

| Área | Capacidad máxima | Costo base |
|------|------------------|------------|
| Soporte Técnico | 50 reclamos/turno | 1 |
| Gerencia de Operaciones/Riesgo | 30 reclamos/turno | 2 |
| Atención al Cliente | 40 reclamos/turno | 1 |

| Prioridad | SLA (horas) | Penalización |
|-----------|-------------|--------------|
| Alta | 2 h | 100 |
| Media | 8 h | 50 |
| Baja | 24 h | 10 |

---

## 🛠️ Tecnologías

### Backend
- **Python 3.10+**
- **FastAPI** — API REST
- **scikit-learn** — Modelo ML (TF-IDF + Regresión Logística)
- **PuLP** — Optimización lineal entera
- **pandas** — Manejo del dataset
- **joblib** — Persistencia de modelos
- **uvicorn** — Servidor ASGI

### Frontend
- **React 18**
- **Vite** — Bundler y servidor de desarrollo
- **Tailwind CSS** — Estilos
- **Lucide React** — Iconos

---

## 🚀 Instalación y Ejecución

### Requisitos previos
- Python 3.10 o superior
- Node.js 18 o superior
- npm

### 1. Backend

```powershell
cd backend

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual (Windows PowerShell)
venv\Scripts\Activate.ps1

# Instalar dependencias
pip install -r ..\requirements.txt

# Ejecutar la API
python main.py
```

La API quedará disponible en: **http://localhost:8000**  
Documentación automática (Swagger): **http://localhost:8000/docs**

### 2. Frontend

En otra terminal:

```powershell
cd frontend

# Instalar dependencias
npm install

# Ejecutar en modo desarrollo
npm run dev
```

La aplicación quedará disponible en: **http://localhost:5173**

---

## 📋 Pasos de Prueba del Sistema

### Prueba 1: Clasificar un reclamo individual

1. Asegúrate de que el backend está corriendo en `http://localhost:8000`
2. Abre el frontend en `http://localhost:5173`
3. En la pestaña **"Nuevo Reclamo"**, escribe un texto de reclamo, por ejemplo:
   > *"No puedo hacer una transferencia, la aplicación me da error de conexión"*
4. Haz clic en **"Clasificar Reclamo"**
5. Verás el resultado: Área (ej. Soporte Técnico) y Prioridad (ej. Alta), junto con las probabilidades por clase

### Prueba 2: Ver historial de reclamos

1. Ve a la pestaña **"Lista de Reclamos"**
2. Deberías ver todos los reclamos clasificados hasta el momento con su área, prioridad y fecha

### Prueba 3: Ejecutar optimización de asignación

1. Asegúrate de haber clasificado al menos un reclamo
2. Ve a la pestaña **"Asignación Óptima"**
3. Haz clic en **"Ejecutar Optimización"**
4. El sistema asignará cada reclamo a un área considerando:
   - La predicción del modelo ML
   - La capacidad máxima de cada área
   - El SLA según la prioridad
   - La confianza del modelo
5. Verás una tabla con el área asignada, área predicha, prioridad, SLA y nivel de confianza

### Prueba 4: Probar endpoints directamente (opcional)

Puedes probar la API desde el navegador en `http://localhost:8000/docs` o con curl:

```powershell
# Clasificar un reclamo
curl -X POST "http://localhost:8000/clasificar" -H "Content-Type: application/json" -d "{\"texto\":\"Mi tarjeta fue bloqueada sin razón\"}"

# Ver información del sistema
curl -X GET "http://localhost:8000/info"

# Listar reclamos
curl -X GET "http://localhost:8000/reclamos"
```

---

## 📁 Estructura del Proyecto

```
enrutamiento-reclamos-banca/
├── .gitignore
├── README.md
├── requirements.txt
├── backend/
│   ├── main.py              # API FastAPI con endpoints /clasificar, /asignar, /reclamos
│   ├── ml_model.py          # Modelo ML: TF-IDF + Regresión Logística
│   ├── optimizacion.py      # Optimización con PuLP (Programación Lineal Entera)
│   ├── modelos/             # Modelos entrenados (.pkl) - se generan al ejecutar
│   └── datos/
│       └── reclamos.csv     # Dataset de 150 reclamos sintéticos en español
└── frontend/
    ├── index.html
    ├── package.json
    ├── vite.config.js
    ├── tailwind.config.js
    ├── postcss.config.js
    └── src/
        ├── main.jsx
        ├── App.jsx
        ├── services/
        │   └── api.js       # Llamadas al backend
        └── components/
            ├── FormularioReclamo.jsx
            └── TablaReclamos.jsx
```

---

## 👥 Colaboradores en GitHub

Para invitar a los integrantes del equipo:

1. Ve al repositorio en GitHub: `https://github.com/Arteezzyy/enrutamiento-reclamos-banca`
2. Haz clic en **Settings** → **Collaborators** (o "Manage access")
3. Haz clic en **Add people**
4. Busca por usuario o email de GitHub de cada integrante
5. Asigna el rol **Write** (pueden subir cambios) o **Admin**
6. Cada integrante recibirá una invitación por correo y debe aceptarla

Cada integrante clona el repositorio con:

```powershell
git clone https://github.com/Arteezzyy/ENRUTAMIENTO-RECLAMOS-BANCA.git
cd ENRUTAMIENTO-RECLAMOS-BANCA
```

---

## 📦 Crear archivo para entrega (ZIP/RAR)

Para entregar el proyecto como archivo comprimido:

```powershell
# Desde la carpeta raíz del proyecto
Compress-Archive -Path * -DestinationPath "../enrutamiento-reclamos-banca.zip"
```

O comprime manualmente la carpeta `enrutamiento-reclamos-banca` en formato `.zip` o `.rar`.

---

## ✅ Avance actual (1° Entrega)

- [x] Dataset de 150 reclamos etiquetados (área + prioridad)
- [x] Modelo ML entrenado con TF-IDF y Regresión Logística
- [x] Métricas de accuracy y F1-score
- [x] API REST con FastAPI
- [x] Módulo de optimización con PuLP
- [x] Frontend en React + Tailwind CSS
- [x] Pruebas funcionales: clasificación, lista y asignación óptima