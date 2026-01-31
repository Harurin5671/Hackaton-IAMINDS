# 👻 GhostEnergy AI - IAMinds 2026

**Plataforma de Optimización Energética Universitaria (UPTC)**

Bienvenido al repositorio oficial de **GhostEnergy AI**. Esta guía está diseñada para que cualquier desarrollador pueda configurar, instalar y ejecutar el proyecto desde cero en menos de 10 minutos.

---

## 📋 1. Requisitos Previos (Prerequisites)

Antes de empezar, asegúrate de tener instalado:
*   **Python 3.9** o superior: [Descargar aquí](https://www.python.org/downloads/)
*   **Git**: [Descargar aquí](https://git-scm.com/downloads)

Verifica tu instalación abriendo una terminal:
```bash
python --version
# Debería decir Python 3.9.x o superior

pip --version
# Debería mostrar la ruta de pip
```

---

## 🛠️ 2. Instalación y Configuración del Entorno

Sigue estos pasos para aislar las dependencias del proyecto:

### 2.1 Clonar el Repositorio
```bash
git clone <URL_DEL_REPOSITORIO>
cd Hackaton-IAMINDS
```

### 2.2 Crear Entorno Virtual (Recomendado)
Es buena práctica no instalar librerías en tu sistema global.
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Mac / Linux
python3 -m venv venv
source venv/bin/activate
```

### 2.3 Instalar Dependencias
```bash
pip install -r requirements.txt
```

---

## 💾 3. Carga de Datos (Importante)

⚠️ **NOTA:** Los archivos de datos (`.csv`) **NO** están en el repositorio por seguridad y tamaño.

Debes conseguir los archivos originales (`consumos_uptc.csv` y `sedes_uptc.csv`) del administrador del proyecto y colocarlos manualmente en la siguiente ruta:

```
Hackaton-IAMINDS/
├── phase-1-exploration/
│   └── data/
│       ├── consumos_uptc.csv   <-- PEGAR AQUÍ
│       └── sedes_uptc.csv      <-- PEGAR AQUÍ
```

---

## 🔑 4. Configurar Variables de Entorno

El proyecto usa Inteligencia Artificial Generativa (Llama-3 vía Groq). Necesitas una API Key.

1.  Crea un archivo llamado `.env` en la raíz del proyecto (junto a este README).
2.  Añade tu clave dentro del archivo:

```bash
# Archivo .env
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

*(Si no tienes una key, pídela al líder del equipo)*

---

## 🚀 5. Ejecución del Pipeline (Paso a Paso)

El sistema es modular. Si es la primera vez que lo corres, debes ejecutar los scripts en orden para generar los archivos de resultados.

### Paso 1: Limpieza de Datos
Genera el dataset limpio `consumos_uptc_clean.csv`.
```bash
python phase-1-exploration/notebooks/02_preprocessing.py
```

### Paso 2: Detección de Anomalías
Identifica fugas y patrones inusuales. Genera `anomalies_detected.csv`.
```bash
python phase-2-anomalies/notebooks/01_detect_anomalies.py
```

### Paso 3: Motor de Recomendaciones (IA)
Prioriza eventos y genera el reporte textual.
```bash
python phase-3-recommendations/notebooks/01_recommendation_logic.py
python phase-3-recommendations/notebooks/02_llm_advisor.py
```

### Paso 4: Cálcular Impacto y Ética
Genera las tramas SHAP y métricas de ahorro.
```bash
python phase-5-explainability/notebooks/01_shap_analysis.py
python phase-5-explainability/notebooks/02_impact_metrics.py
```

---

## 🖥️ 6. Lanzar el Dashboard

Una vez generados los datos, levanta la interfaz gráfica:

```bash
streamlit run phase-4-interface/app/dashboard.py
```

El navegador abrirá automáticamente `http://localhost:8501`.

---

## 🧩 Estructura del Proyecto para Desarrolladores

*   **`phase-1-exploration/`**: Scripts de ingeniería de datos (`pandas`, `xgboost`).
*   **`phase-2-anomalies/`**: Algoritmos no supervisados (`IsolationForest`).
*   **`phase-3-recommendations/`**: Lógica de priorización y llamadas a LLM (`LangChain`).
*   **`phase-4-interface/`**: Código de la aplicación web (`Streamlit`).
*   **`phase-5-explainability/`**: Análisis de transparencia (`SHAP`).
*   **`results/`**: Carpetas dentro de cada fase donde se guardan los outputs intermedios.

---

## ❓ Solución de Problemas (Troubleshooting)

*   **Error: `FileNotFoundError: ... consumos_uptc.csv`**
    *   *Solución*: Ver el paso **3. Carga de Datos**. Te falta copiar el archivo CSV.
*   **Error: `API Key no configurada` en el Dashboard**
    *   *Solución*: Ver el paso **4**. Asegúrate de que el archivo se llame `.env` (con el punto al inicio) y no `.env.txt`.
*   **Error: `ModuleNotFoundError`**
    *   *Solución*: Asegúrate de haber activado el entorno virtual (`source venv/bin/activate`) antes de correr los comandos.

---
*Hackathon IAMinds 2026 - Equipo NeuronalCoders*
