# 👻 GhostEnergy AI - IAMinds 2026

**Plataforma de Optimización Energética Universitaria (UPTC)**

Este proyecto es una solución integral de Inteligencia Artificial diseñada para predecir, detectar y mitigar el desperdicio energético en campus universitarios. Se divide en 5 fases modulares, desde la exploración de datos hasta la interfaz de usuario.

---

## 🚀 Guía de Inicio Rápido (Quick Start)

### 1. Instalación
Asegúrate de tener Python 3.9+ instalado.
```bash
# 1. Clonar repositorio
git clone <tu-repo>
cd Hackaton-IAMINDS

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar Variables de Entorno
# Crea un archivo .env en la raíz con tu API Key de Groq:
# GROQ_API_KEY=gsk_...
```

### 2. Ejecutar la Demo Completa
Para ver el resultado final (Dashboard Interactivo):
```bash
streamlit run phase-4-interface/app/dashboard.py
```

---

## 📚 Documentación Detallada por Fases

### 🔷 Fase 1: Exploración y Modelado Predictivo
**Objetivo:** Entender los datos históricos y entrenar un modelo capaz de predecir el consumo futuro.

*   **¿Qué hace?**
    *   Limpia los datos (`02_preprocessing.py`): Imputa valores nulos, corrige negativos.
    *   Entrena un modelo (`03_model_training.py`): Aprende la relación entre Hora, Ocupación, Temperatura y Consumo.
*   **Herramientas & Por qué:**
    *   **Pandas/Numpy:** Estándar para manipulación de datos tabulares.
    *   **XGBoost (Extreme Gradient Boosting):** Elegido por su altísimo rendimiento en datos tabulares estructurados y capacidad para manejar relaciones no lineales mejor que una regresión lineal simple.
*   **Archivos Clave:**
    *   `phase-1-exploration/data/consumos_uptc_clean.csv`: Dataset limpio.
    *   `phase-1-exploration/notebooks/03_model_training.py`: Script de entrenamiento (RMSE Global: ~2-5 kWh error).

### 🔷 Fase 2: Detección de Anomalías
**Objetivo:** Identificar patrones de consumo inusuales (fugas, equipos encendidos, desperdicio).

*   **¿Qué hace?**
    *   **Detección Estadística:** Compara el consumo real vs. el predicho por XGBoost (Residuo).
    *   **Detección IA (No supervisada):** Usa **Isolation Forest** para encontrar outliers multidimensionales.
    *   **Reglas de Negocio:** Detecta "Consumo Fantasma" (Alta energía con ocupación < 5%).
*   **Herramientas & Por qué:**
    *   **Isolation Forest:** Ideal para detectar anomalías en datasets grandes sin necesidad de etiquetas previas (unsupervised).
*   **Archivos Clave:**
    *   `phase-2-anomalies/results/anomalies_detected.csv`: Lista de cada hora anómala identificada.

### 🔷 Fase 3: Motor de Recomendaciones (IA Generativa)
**Objetivo:** Traducir los datos técnicos en acciones humanas comprensibles.

*   **¿Qué hace?**
    *   Agrupa anomalías individuales en "Eventos" (ej: Ineficiencia continua de 4 horas).
    *   Envía el contexto (Sede, kWh desperdiciados, Hora) a un **LLM (Llama-3)**.
    *   Genera una "Tarjeta de Acción" con diagnóstico y pasos a seguir.
*   **Herramientas & Por qué:**
    *   **LangChain + Groq (Llama-3-70b):** Groq ofrece inferencia casi instantánea, vital para dashboards en tiempo real. Llama-3 tiene excelente razonamiento en español.
*   **Archivos Clave:**
    *   `phase-3-recommendations/results/advisor_report.md`: Reporte narrativo generado por la IA.

### 🔷 Fase 4: Interfaz de Usuario (Dashboard)
**Objetivo:** Centralizar la información para el Gestor de Facilidades.

*   **¿Qué hace?**
    *   Visualiza KPIs (Ahorro potencial, Alertas activas).
    *   Muestra mapas de calor de anomalías.
    *   Incluye un **Chatbot (XAI)** para interrogar a los datos ("¿Por qué Tunja está en rojo?").
*   **Herramientas & Por qué:**
    *   **Streamlit:** Permite desplegar aplicaciones de datos interactivas en Python en minutos, sin saber HTML/CSS.
*   **Cómo usuarlo:** Navega entre pestañas para ver Analítica vs. Recomendaciones. Escribe en el chat para recibir insights de la IA.

### 🔷 Fase 5: Explicabilidad y Ética
**Objetivo:** Garantizar confianza y transparencia.

*   **¿Qué hace?**
    *   Calcula valores **SHAP** para explicar *qué variables* (Ocupación, Hora) causaron una predicción.
    *   Estima el impacto ambiental (CO2) y económico.
    *   Documenta los límites del modelo.
*   **Herramientas & Por qué:**
    *   **SHAP (SHapley Additive exPlanations):** El estándar de oro en la industria para explicar modelos de "caja negra" como XGBoost.
*   **Archivos Clave:**
    *   `phase-5-explainability/docs/ETHICS.md`: Carta de transparencia del modelo.

---

## 📂 Estructura del Proyecto

```
Hackaton-IAMINDS/
├── requirements.txt
├── phase-1-exploration/      # Datos y Modelado
├── phase-2-anomalies/        # Detección de Fugas/Outliers
├── phase-3-recommendations/  # Agente IA (Groq)
├── phase-4-interface/        # App Streamlit
└── phase-5-explainability/   # Ética y SHAP
```

*Hecho por NeuronalCoders - 2026*
