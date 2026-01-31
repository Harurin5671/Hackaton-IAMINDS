# Fase 2: Detección de Anomalías y Patrones de Ineficiencia Energética

## 🎯 Visión General

La Fase 2 se especializa en la identificación automática de situaciones de desperdicio energético, patrones operativos ineficientes y valores atípicos inusuales en los campus universitarios de la UPTC. Esta fase complementa el modelado predictivo de la Fase 1 mediante la aplicación de técnicas avanzadas de detección de anomalías y análisis de ineficiencias operativas.

## 🔍 Estrategia Híbrida de Detección

Implementamos un enfoque híbrido que combina **Machine Learning No Supervisado** con **Heurísticas Basadas en Reglas** para una detección completa y precisa de anomalías energéticas.

### **📊 Enfoques Implementados**

#### **A. Detección Basada en IA (Isolation Forest)**
- **Objetivo**: Identificar valores atípicos que se desvían significativamente de la distribución multivariante "normal"
- **Algoritmo**: Isolation Forest con contaminación del 2%
- **Características**: `energia_total_kwh`, `ocupacion_pct`, `hour`, `dayofweek`
- **Caso de Uso**: Detección de picos o caídas inexplicables (fallas de equipos, fugas)

#### **B. Análisis de Residuos Basado en Modelo**
- **Objetivo**: Aprovechar el Modelo Predictivo de la Fase 1
- **Lógica**: Si `Consumo Real` >> `Consumo Predicho`, sugiere anomalía donde se usa energía sin justificación estándar
- **Métrica**: `Residuo = Real - Predicho`. Umbral: > 2 Desviaciones Estándar

#### **C. Ineficiencia Basada en Reglas (Conocimiento del Dominio)**
- **Objetivo**: Detectar "malas prácticas" conocidas
- **Reglas Implementadas**:
  1. **"Consumo Fantasma"**: Alto consumo con `ocupacion_pct` cercano a 0%
  2. **"Desperdicio Nocturno"**: Alto consumo en sectores académicos (Salones, Auditorios) entre 10 PM - 5 AM
  3. **"Operaciones de Fin de Semana"**: Consumo elevado en oficinas/salones los domingos

## 📁 Estructura del Proyecto

```
phase-2-anomalies/
├── docs/
│   └── PLAN_PHASE_2.md                    # Planificación y estrategia original
├── notebooks/
│   ├── 01_detect_anomalies.py             # Script principal de detección de anomalías
│   └── 02_analyze_inefficiencies.py       # Script de análisis de ineficiencias
├── results/
│   ├── anomalies_detected.csv             # Dataset completo con anomalías detectadas
│   ├── critical_anomalies_scatter.html     # Visualización interactiva de anomalías críticas
│   ├── detailed_inefficiencies.csv        # Análisis detallado de ineficiencias
│   └── waste_summary.csv                   # Resumen cuantificado de desperdicio energético
└── README.md                              # Este archivo
```

## 🚀 Inicio Rápido

### Prerrequisitos
El proyecto utiliza dependencias centralizadas en el requirements.txt del proyecto principal Hackaton-IAMINDS.

```bash
# Instalar dependencias desde la raíz del proyecto
cd /ruta/al/proyecto/Hackaton-IAMINDS
pip install -r requirements.txt
```

### Pipeline de Detección de Anomalías
```bash
# Navegar a la fase 2
cd phase-2-anomalies

# 1. Detección de Anomalías (Machine Learning + Residuos)
python notebooks/01_detect_anomalies.py

# 2. Análisis de Ineficiencias (Reglas de Negocio)
python notebooks/02_analyze_inefficiencies.py
```

## 🔧 Características Técnicas Detalladas

### **Detección de Anomalías (`01_detect_anomalies.py`)**

#### **Análisis de Residuos**
- **Modelo de Referencia**: XGBoost Regressor (100 estimadores, profundidad 5)
- **Características**: Codificación cíclica temporal + temperatura + ocupación
- **Umbral de Anomalía**: Residuo > 2 desviaciones estándar
- **Lógica**: Detecta consumo anormalmente alto respecto al patrón esperado

#### **Isolation Forest**
- **Contaminación**: 2% (asunción de anomalías raras)
- **Entrenamiento**: Por sede individual para manejar diferentes escalas
- **Características**: Consumo total, ocupación, hora, día de semana
- **Clasificación**: -1 (anomalía), 1 (normal)

#### **Anomalías Críticas**
- **Definición**: Intersección de ambos métodos (Residuos + Isolation Forest)
- **Precisión**: Solo se marcan como críticas las anomalías detectadas por ambos métodos
- **Ventaja**: Reduce falsos positivos mediante consenso de métodos

### **Análisis de Ineficiencias (`02_analyze_inefficiencies.py`)**

#### **Consumo Fantasma**
- **Definición**: Consumo en percentil 75 con ocupación < 5%
- **Lógica**: Detecta energía consumida sin presencia humana justificable
- **Impacto**: Identifica equipos encendidos innecesariamente

#### **Desperdicio Nocturno**
- **Definición**: Consumo > 50 kWh en áreas académicas entre 23:00-05:00
- **Sectores**: Salones y Auditorios (áreas que deberían estar inactivas)
- **Umbral**: 50 kWh como heurística para "luces dejadas encendidas"

## 📈 Archivos de Salida Generados

### **Principal: `anomalies_detected.csv`**
- **Registros**: 275,388 mediciones analizadas
- **Columnas de Anomalía**:
  - `anomaly_residual`: Booleano (residuos > 2σ)
  - `anomaly_iso`: Entero (0/1, Isolation Forest)
  - `anomaly_critical`: Entero (0/1, consenso de ambos métodos)
- **Predicciones**: `predicted_consumption`, `residual`

### **Visualización: `critical_anomalies_scatter.html`**
- **Gráfico**: Scatter plot interactivo de anomalías críticas
- **Dimensiones**: Timestamp vs Consumo Energético
- **Color**: Por sede para identificación geográfica
- **Formato**: HTML interactivo con Plotly

### **Análisis Detallado: `detailed_inefficiencies.csv`**
- **Flags de Ineficiencia**:
  - `phantom_waste`: Booleano (consumo fantasma detectado)
  - `night_waste`: Booleano (desperdicio nocturno detectado)
- **Métricas**: Consumo por sector, timestamps, condiciones

### **Resumen de Impacto: `waste_summary.csv`**
- **Categorías**: Consumo Fantasma, Desperdicio Nocturno
- **Métricas**:
  - `Total_kWh_Wasted`: Energía desperdiciada por categoría
  - `Cost_Est_COP`: Costo estimado en pesos colombianos (800 COP/kWh)

## 📊 Insights Clave Descubiertos

### **Patrones de Anomalías Identificados**
- **Anomalías por Residuos**: Desviaciones significativas del consumo esperado
- **Anomalías por Isolation Forest**: Valores atípicos multivariantes
- **Anomalías Críticas**: Eventos anómalos validados por múltiples métodos

### **Ineficiencias Operativas**
- **Consumo Fantasma**: 4,885.44 kWh detectados en condiciones de baja ocupación
- **Costo Estimado**: ~3.9 millones de pesos colombianos en consumo fantasma
- **Desperdicio Nocturno**: Monitoreo continuo de áreas académicas fuera de horario

### **Hallazgos por Sede**
- **Escalabilidad**: Detección adaptada a diferentes escalas de consumo por sede
- **Patrones Específicos**: Cada campus muestra patrones de anomalía únicos
- **Oportunidades**: Identificación de áreas específicas para optimización

## 🔍 Metodología de Validación

### **Doble Verificación**
- **Consenso de Métodos**: Solo anomalías críticas requieren validación por ambos métodos
- **Reducción de Falsos Positivos**: Estrategia para minimizar alertas innecesarias
- **Priorización**: Enfoque en anomalías críticas para acción inmediata

### **Análisis Temporal**
- **Patrones Horarios**: Detección de anomalías específicas por hora del día
- **Patrones Diarios**: Identificación de tendencias semanales
- **Patrones Estacionales**: Monitoreo de variaciones estacionales

## 📚 Dependencias del Sistema

### **Librerías Principales**
- **pandas**: Manipulación y análisis de datos
- **numpy**: Operaciones numéricas eficientes
- **scikit-learn**: Isolation Forest para detección de anomalías
- **xgboost**: Modelo predictivo para análisis de residuos
- **plotly**: Visualizaciones interactivas

### **Dependencias de Datos**
- **Datos de Entrada**: `consumos_uptc_clean.csv` (Fase 1)
- **Procesamiento**: Requiere datos limpios y preprocesados
- **Salidas**: Múltiples formatos (CSV, HTML)

## 🎯 Impacto y Beneficios para la UPTC

### **Optimización Energética**
- **Reducción de Costos**: Identificación concreta de desperdicios energéticos
- **Mantenimiento Predictivo**: Detección temprana de fallas de equipos
- **Operaciones Eficientes**: Optimización de horarios y uso de instalaciones

### **Sostenibilidad Ambiental**
- **Reducción de Huella de Carbono**: Identificación de consumo innecesario
- **Uso Responsable**: Promoción de prácticas energéticas sostenibles
- **Reportabilidad**: Métricas claras de impacto ambiental

### **Toma de Decisiones**
- **Alertas Proactivas**: Detección automática de problemas
- **Priorización de Acciones**: Enfoque en anomalías críticas
- **Métricas Cuantificables**: Impacto medible en kWh y costos

## 🔧 Especificaciones Técnicas

### **Configuración de Modelos**
- **Isolation Forest**: contamination=0.02, random_state=42
- **XGBoost**: n_estimators=100, max_depth=5, n_jobs=-1
- **Umbral de Residuos**: 2 desviaciones estándar
- **Umbral de Consumo Nocturno**: 50 kWh

### **Procesamiento de Datos**
- **Entrada**: CSV limpio de Fase 1 (275K+ registros)
- **Procesamiento**: Por sede para manejar escalas diferentes
- **Salida**: Múltiples archivos con diferentes niveles de detalle

### **Rendimiento**
- **Escalabilidad**: Procesamiento eficiente de grandes datasets
- **Memoria**: Optimizado para manejo de datos temporales
- **Velocidad**: Paralelización con n_jobs=-1

## 📈 Métricas de Evaluación

### **Detección de Anomalías**
- **Precisión**: Validación mediante doble método
- **Cobertura**: Análisis completo de dataset histórico
- **Especificidad**: Reducción de falsos positivos

### **Análisis de Ineficiencias**
- **Cuantificación**: Medición exacta de kWh desperdiciados
- **Impacto Económico**: Conversión a costos en moneda local
- **Identificación**: Localización específica de problemas

## 🚧 Próximos Pasos del Proyecto

### **Integración con Fase 3**
- **Sistema de Alertas**: Implementación de notificaciones en tiempo real
- **Dashboard Interactivo**: Visualización continua de anomalías
- **API de Detección**: Endpoints para consulta de anomalías recientes

### **Mejora Continua**
- **Ajuste de Umbrales**: Optimización basada en retroalimentación
- **Nuevas Reglas**: Incorporación de patrones de ineficiencia adicionales
- **Validación Humana**: Proceso de verificación de anomalías detectadas

### **Despliegue en Producción**
- **Monitoreo Continuo**: Ejecución automatizada de detección
- **Reportes Automáticos**: Generación periódica de informes
- **Integración con Sistemas**: Conexión con sistemas de gestión universitaria

## 🤝 Guía de Contribución

### **Estilo de Código**
- Código limpio y documentado siguiendo PEP 8 de Python
- Funciones modulares con responsabilidades claras
- Manejo robusto de errores y validación de datos
- Comentarios explicativos para lógica compleja

### **Validación de Resultados**
- Verificación cruzada de anomalías detectadas
- Análisis cualitativo de patrones identificados
- Benchmarking con métodos alternativos
- Pruebas de sensibilidad en umbrales

## 📄 Licencia

Este proyecto es parte de la iniciativa Hackaton-IAMINDS para la optimización de la gestión energética de la UPTC.

## 📞 Contacto y Soporte

Para preguntas sobre la Fase 2 de detección de anomalías:
- **Repositorio del Proyecto**: `/phase-2-anomalies`
- **Planificación Original**: Consultar `docs/PLAN_PHASE_2.md`
- **Scripts Principales**: Revisar `notebooks/01_detect_anomalies.py` y `notebooks/02_analyze_inefficiencies.py`
- **Resultados**: Explorar archivos en `results/`

## 🎯 Impacto y Beneficios

### **Beneficios Operativos**
- **Detección Temprana**: Identificación proactiva de problemas energéticos
- **Reducción de Costos**: Ahorro significativo mediante eliminación de desperdicios
- **Mantenimiento Predictivo**: Anticipación de fallas de equipos

### **Beneficios Estratégicos**
- **Decisiones Basadas en Datos**: Información concreta para gestión energética
- **Sostenibilidad**: Contribución a objetivos ambientales institucionales
- **Innovación Tecnológica**: Aplicación práctica de IA en gestión universitaria

### **Innovación Metodológica**
- **Enfoque Híbrido**: Combinación de ML y reglas de negocio
- **Validación Cruzada**: Doble verificación para mayor precisión
- **Escalabilidad**: Sistema adaptable a múltiples campus

---

**Nota Importante**: Esta fase establece las capacidades de detección inteligente para el sistema Hackaton-IAMINDS. Las fases subsecuentes construyen sobre este trabajo de detección para entregar capacidades de monitoreo continuo y optimización energética en tiempo real.

**Versión**: 1.0 | **Última Actualización**: 2026 | **Estado**: Completo y Validado
