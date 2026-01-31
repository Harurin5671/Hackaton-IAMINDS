# Fase 1: Exploración y Modelado Predictivo

## 🎯 Visión General

La Fase 1 se centra en el análisis exploratorio de datos, preprocesamiento y desarrollo de modelos de machine learning para la predicción del consumo energético en los campus universitarios de la UPTC. Esta fase establece los cimientos del sistema GhostEnergy AI mediante el análisis de patrones históricos de consumo y la construcción de modelos predictivos precisos.

## 📊 Información del Dataset

### Fuentes de Datos
- **Dataset Principal**: `consumos_uptc.csv` (46.9MB) - Datos crudos históricos
- **Dataset Limpio**: `consumos_uptc_clean.csv` (79.1MB) - Datos procesados y enriquecidos
- **Metadatos de Campus**: `sedes_uptc.csv` - Información estructural de cada sede

### Cobertura de Datos
- **Periodo Temporal**: 2018-2025 (Mediciones cada hora)
- **Campus Universitarios**: 5 sedes de la UPTC
- **Variables Disponibles**: Consumo energético, temperatura, ocupación, emisiones de CO₂
- **Sectores Analizados**: Comedores, Salones, Laboratorios, Auditorios, Oficinas

### Características Clave
- **Temporales**: Hora, día, mes, períodos académicos
- **Ambientales**: Temperatura externa, porcentajes de ocupación
- **Estructurales**: Área del campus, población estudiantil, altitud
- **Consumo**: Energía por sector, consumo total, huella de carbono

## 🚀 Inicio Rápido

### Prerrequisitos
El proyecto utiliza dependencias centralizadas en el requirements.txt del proyecto principal Hackaton-IAMINDS.

```bash
# Instalar dependencias desde la raíz del proyecto
cd /ruta/al/proyecto/Hackaton-IAMINDS
pip install -r requirements.txt
```

### Pipeline de Procesamiento de Datos
```bash
# Navegar a la fase 1
cd phase-1-exploration

# 1. Análisis Exploratorio de Datos (EDA)
python notebooks/01_eda_clean.py

# 2. Preprocesamiento de Datos y Feature Engineering
python notebooks/02_preprocessing_clean.py

# 3. Entrenamiento del Modelo y Generación de Pronósticos
python notebooks/03_model_training_clean.py
```

## 📁 Estructura del Proyecto

```
phase-1-exploration/
├── data/
│   ├── consumos_uptc.csv              # Datos históricos crudos
│   ├── consumos_uptc_clean.csv        # Datos procesados y limpios
│   └── sedes_uptc.csv                 # Metadatos de los campus
├── notebooks/
│   ├── 01_eda_clean.py                # Análisis exploratorio completo
│   ├── 02_preprocessing_clean.py      # Pipeline de preprocesamiento
│   └── 03_model_training_clean.py      # Entrenamiento del modelo ML
├── docs/
│   ├── DATA_DICTIONARY.md             # Definición detallada de variables
│   ├── PLAN_PHASE_1.md                # Planificación original del proyecto
│   ├── eda_plots/                     # Visualizaciones del análisis exploratorio
│   └── model_plots/                   # Salidas y gráficos del modelo
└── README.md                          # Este archivo
```

## 🔍 Características del Análisis de Datos

### Análisis Exploratorio (`01_eda_clean.py`)
- **Evaluación de Calidad de Datos**: Valores faltantes, outliers, duplicados
- **Patrones Temporales**: Tendencias de consumo horarias, diarias, mensuales
- **Análisis por Sectores**: Desglose energético por sectores de cada campus
- **Análisis de Correlaciones**: Relación temperatura, ocupación vs. consumo
- **Visualizaciones Interactivas**: Gráficos Plotly guardados en formato HTML

### Pipeline de Preprocesamiento (`02_preprocessing_clean.py`)
- **Limpieza de Datos**: Manejo de valores negativos, interpolación de faltantes
- **Ingeniería de Características**: Codificación cíclica para variables temporales
- **Remoción de Outliers**: Filtrado basado en cuantiles (percentil 1-99)
- **Preparación de Series Temporales**: Ordenamiento y agrupación adecuados

### Entrenamiento del Modelo (`03_model_training_clean.py`)
- **Algoritmo**: XGBoost Regressor con hiperparámetros optimizados
- **Características**: 15+ features engineering incluyendo lags y codificación cíclica
- **Validación**: División temporal (2018-2024 entrenamiento, 2025 prueba)
- **Generación de Pronósticos**: Predicciones completas para 2026 por hora

## 🤖 Modelo de Machine Learning

### Arquitectura del Modelo
- **Tipo**: Gradient Boosting (XGBoost) - Algoritmo de árboles de decisión optimizado
- **Variable Objetivo**: `energia_total_kwh` (Consumo total de energía)
- **Características de Entrada**: 15+ variables engineered
- **Datos de Entrenamiento**: 7 años de datos históricos horarios

### Ingeniería de Características Detallada
```python
# Características Temporales (Codificación Cíclica)
- hour_sin, hour_cos          # Codificación cíclica de la hora
- day_sin, day_cos            # Codificación cíclica del día de la semana  
- month_sin, month_cos        # Codificación cíclica del mes

# Características de Lag (Historial)
- lag_1h                      # Consumo de la hora anterior
- lag_24h                     # Consumo del día anterior
- lag_168h                    # Consumo de la semana anterior

# Características Contextuales
- temperatura_exterior_c      # Temperatura externa en grados Celsius
- ocupacion_pct               # Porcentaje de ocupación del campus
- es_dia_laboral              # Indicador de día laboral (Lun-Vie)
- area_m2, num_estudiantes    # Características físicas del campus
```

### Rendimiento del Modelo
- **RMSE de Entrenamiento**: Optimizado para error mínimo
- **RMSE de Prueba**: Validado con datos de 2025
- **MAE**: Métricas de error absoluto medio
- **Importancia de Características**: Análisis incorporado de XGBoost

## 📈 Generación de Pronósticos

### Archivos de Salida Generados
- **Principal**: `forecast_2026_full.csv` - Predicciones horarias para todo 2026
- **Visualización**: `forecast_2026_plot.html` - Gráficos interactivos del pronóstico
- **Validación**: Comparación entre datos reales 2025 vs. predichos 2026

### Cobertura de los Pronósticos
- **Resolución Temporal**: Predicciones cada hora (8,760 horas totales)
- **Cobertura Geográfica**: Todas las 5 sedes de la UPTC
- **Desglose por Sectores**: Consumo total de energía por campus
- **Rango Temporal**: 1 de enero 2026 - 31 de diciembre 2026

## 📊 Insights Clave Descubiertos

### Patrones de Consumo Identificados
- **Horas Pico**: Mayor consumo durante horas académicas (8am-6pm)
- **Variación Estacional**: Patrones de consumo dependientes de la temperatura
- **Diferencias entre Campus**: Consumo variable según tamaño e instalaciones
- **Calendario Académico**: Reducción significativa durante períodos vacacionales

### Hallazgos del Modelo
- **Predictores Fuertes**: Temperatura, ocupación, lags históricos son los más importantes
- **Ciclos Temporales**: Patrones diarios y estacionales capturados efectivamente
- **Especificidad por Campus**: Cada sede requiere consideración individual
- **Importancia de Features**: Las características de lag son las más predictivas

## 🔧 Especificaciones Técnicas

### Dependencias del Sistema
- **Python 3.8+** - Lenguaje de programación principal
- **pandas** - Manipulación y análisis de datos
- **numpy** - Operaciones numéricas eficientes
- **xgboost** - Algoritmo de machine learning
- **scikit-learn** - Métricas y herramientas de preprocesamiento
- **plotly** - Visualizaciones interactivas

### Consideraciones de Rendimiento
- **Memoria**: Optimizado para procesamiento de datasets grandes
- **Computación**: Procesamiento paralelo con XGBoost
- **Almacenamiento**: Formatos CSV eficientes para salida
- **Visualización**: Gráficos HTML interactivos

## 📚 Documentación Complementaria

### Diccionario de Datos
Consultar `docs/DATA_DICTIONARY.md` para definiciones detalladas de todas las variables y su significado.

### Plan del Proyecto
Revisar `docs/PLAN_PHASE_1.md` para la documentación original de planificación del proyecto.

### Salidas del Análisis
- **Gráficos EDA**: `docs/eda_plots/` - Visualizaciones del análisis exploratorio
- **Gráficos del Modelo**: `docs/model_plots/` - Visualizaciones de rendimiento y pronósticos

## 🚧 Próximos Pasos del Proyecto

### Integración con Fase 2
- **Desarrollo de API**: Endpoints RESTful para acceso a pronósticos
- **Procesamiento en Tiempo Real**: Capacidades de integración con datos en vivo
- **Optimización del Modelo**: Tuning de hiperparámetros y métodos de ensemble
- **Validación Cruzada**: Validación del modelo entre diferentes campus

### Despliegue en Producción
- **Servicio del Modelo**: Endpoints API para consumo de pronósticos
- **Monitoreo**: Seguimiento del rendimiento del modelo
- **Reentrenamiento**: Pipeline automatizado de actualización del modelo
- **Escalabilidad**: Estrategia de despliegue multi-campus

## 🤝 Guía de Contribución

### Estilo de Código
- Código limpio y comentado siguiendo PEP 8 de Python
- Funciones modulares con responsabilidades claras
- Manejo de errores y validación robusta
- Uso eficiente de memoria para datasets grandes

### Pruebas y Validación
- Verificación de calidad de datos
- Benchmarks de rendimiento del modelo
- Procedimientos de validación cruzada
- Pruebas fuera de muestra (out-of-sample)

## 📄 Licencia

Este proyecto es parte de la iniciativa GhostEnergy AI para la optimización de la gestión energética de la UPTC.

## 📞 Contacto y Soporte

Para preguntas sobre la Fase 1 de exploración y modelado:
- **Repositorio del Proyecto**: `/phase-1-exploration`
- **Problemas con Datos**: Consultar `docs/DATA_DICTIONARY.md`
- **Preguntas del Modelo**: Revisar `03_model_training_clean.py`
- **Soporte Técnico**: Revisar la documentación en `docs/`

## 🎯 Impacto y Beneficios

### Beneficios para la UPTC
- **Optimización Energética**: Reducción de costos mediante predicciones precisas
- **Planificación Estratégica**: Mejor asignación de recursos energéticos
- **Sostenibilidad**: Reducción de huella de carbono mediante gestión eficiente
- **Toma de Decisiones**: Información basada en datos para administración

### Innovación Tecnológica
- **Inteligencia Artificial**: Aplicación práctica de ML en gestión universitaria
- **Análisis Predictivo**: Anticipación de necesidades energéticas
- **Visualización de Datos**: Herramientas interactivas para análisis
- **Escalabilidad**: Sistema preparado para expansión futura

---

**Nota Importante**: Esta fase establece los cimientos de ciencia de datos para el sistema GhostEnergy AI. Las fases subsecuentes construyen sobre este trabajo exploratorio para entregar capacidades de pronóstico energético y optimización listas para producción.

**Versión**: 1.0 | **Última Actualización**: 2026 | **Estado**: Completo y Validado
