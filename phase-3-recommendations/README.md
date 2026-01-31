# Fase 3: Motor Inteligente de Recomendaciones Energéticas

## 🎯 Visión General

La Fase 3 se especializa en transformar las anomalías e ineficiencias detectadas en recomendaciones accionables y comprensibles para gestores de instalaciones universitarias. Este módulo funciona como un consultor estratégico de energía que traduce datos técnicos en decisiones de negocio claras.

## 🧠 Estrategia Híbrida: Motor de Reglas + Sistema Experto

Implementamos un enfoque dual que combina **reglas determinísticas** (para precisión) con **sistema experto basado en conocimiento** (para explicabilidad y contexto humano), creando recomendaciones que tanto ingenieros como directivos pueden entender y actuar.

### **📋 Arquitectura del Sistema**

#### **Capa de Activación (Motor de Regras)**
Clasifica cada anomalía en "Escenarios" específicos:
1. **Escenario 1: "Consumo Fantasma"** (Alta Energía / Baja Ocupación)
2. **Escenario 2: "Búho Nocturno"** (Uso académico a horas inusuales)
3. **Escenario 3: "Rompe-Picos"** (Excediendo capacidad máxima)
4. **Escenario 4: "Fuga de Refrigeración"** (Alta correlación con temperatura pero magnitud inesperada)

#### **Capa Generadora (Sistema Experto)**
Transforma metadatos del escenario en "Tarjetas de Notificación" comprensibles:
- **Motor de Recomendaciones**: Basado en conocimiento específico del dominio energético
- **Plantillas Estructuradas**: Formatos probados para comunicación efectiva
- **Salida**: Consejos en lenguaje natural con impacto económico

## 📁 Estructura del Proyecto

```
phase-3-recommendations/
├── docs/
│   ├── PLAN_PHASE_3.md                    # Planificación original del motor
│   └── PLAN_PHASE_3_IMPROVED.md           # Versión mejorada con enfoque ejecutivo
├── notebooks/
│   ├── 01_recommendation_logic.py         # Lógica de clasificación y agrupación
│   └── 02_llm_advisor.py                  # Motor de generación con LLM
├── results/
│   ├── prioritized_recommendations.csv    # Eventos priorizados con recomendaciones IA
│   └── advisor_report.md                  # Reporte estratégico.         
└── README.md                              # Este archivo
```

## 🚀 Inicio Rápido

### Prerrequisitos
El proyecto utiliza dependencias centralizadas y requiere configuración de APIs externas:

```bash
# Instalar dependencias desde la raíz del proyecto
cd /ruta/al/proyecto/Hackaton-IAMINDS
pip install -r requirements.txt

# Configurar variable de entorno para el motor de recomendaciones
export GROQ_API_KEY="tu-api-key-groq"
```

### Pipeline de Recomendaciones
```bash
# Navegar a la fase 3
cd phase-3-recommendations

# 1. Lógica de Recomendaciones (Clasificación y Agrupación)
python notebooks/01_recommendation_logic.py

# 2. Generador de Reportes (Motor de Recomendaciones)
python notebooks/02_llm_advisor.py
```

## 🔧 Características Técnicas Detalladas

### **Lógica de Recomendaciones (`01_recommendation_logic.py`)**

#### **Clasificación Inteligente de Anomalías**
- **Consumo Fantasma**: Ocupación < 5% con consumo anómalo
- **Uso Nocturno Inusual**: Horas > 22PM o < 5AM con actividad
- **Pico de Demanda Inesperado**: Consumo alto durante horas pico pero anómalo

#### **Agregación de Eventos**
- **Agrupación Inteligente**: Eventos consecutivos dentro de 3 horas se agrupan
- **Identificación Única**: `sede_event_id` para seguimiento
- **Priorización por Impacto**: Ranking por kWh totales consumidos

#### **Métricas Calculadas**
- **Duración**: Horas consecutivas del evento
- **Impacto Energético**: Total kWh consumidos
- **Contexto**: Ocupación promedio durante el evento

### **Asesor de Recomendaciones (`02_llm_advisor.py`)**

#### **Motor de Generación de Recomendaciones**
- **Sistema Experto**: Basado en conocimiento específico del dominio energético
- **Plantillas Estructuradas**: Formatos consistentes para comunicación efectiva
- **Tono Profesional**: Directo, urgente, sin jerga técnica

#### **Base de Conocimiento Integrada**
- **Cocinas**: Sugerencias sobre congeladores industriales, hornos
- **Aulas**: Luces, proyectores, aire acondicionado
- **Laboratorios**: Centrífugas, compresores, campanas de humo
- **Oficinas**: Computadoras, calentadores personales

#### **Motor de Procesamiento**
- **Procesamiento Principal**: Groq para generación eficiente
- **Respaldo**: Templates de texto robustos si el servicio no está disponible

## 📈 Archivos de Salida Generados

### **Principal: `prioritized_recommendations.csv`**
- **Registros**: 1,313 eventos procesados
- **Columnas Principales**:
  - `event_id`: Identificador único del evento
  - `sede`: Campus universitario
  - `start_time/end_time`: Duración del evento
  - `total_kwh`: Impacto energético total
  - `avg_occupancy`: Contexto de ocupación
  - `category`: Tipo de anomalía clasificada
  - `duration_hours`: Duración en horas
  - `ai_recommendation`: Recomendación generada por el sistema

### **Reporte Estratégico: `advisor_report.md`**
- **Formato**: Markdown con tarjetas de incidente crítico
- **Estructura por Evento**:
  - **🚨 Headline**: Título llamativo en español
  - **📉 ¿Qué pasó?**: Explicación simple y clara
  - **💸 El Costo**: Impacto económico en pesos colombianos
  - **🛠️ Solución Inmediata**: Pasos accionables
  - **🔮 Estrategia a Largo Plazo**: Recomendaciones estratégicas

## 📊 Insights Clave del Sistema

### **Patrones de Recomendación Identificados**
- **Eventos Críticos**: Priorizados por impacto económico (>200,000 COP por evento)
- **Concentración Geográfica**: Sogamoso y Duitama con mayor frecuencia de eventos
- **Tipos Dominantes**: Picos de demanda inesperados como categoría principal
- **Ventanas de Tiempo**: Eventos típicamente de 4-6 horas de duración

### **Impacto Económico Cuantificado**
- **Costo por Evento**: Promedio 150,000 - 250,000 COP
- **Potencial de Ahorro**: Identificación de oportunidades específicas
- **ROI de Acciones**: Medición clara del impacto de recomendaciones

### **Recomendaciones Personalizadas**
- **Por Sector**: Acciones específicas según tipo de instalación
- **Por Contexto**: Considerando ocupación y horarios
- **Por Impacto**: Priorizando acciones de mayor retorno

## 🔍 Metodología de Generación de Recomendaciones

### **Análisis Contextual**
- **Datos Temporales**: Timestamps para contexto horario
- **Datos de Ocupación**: Porcentaje de presencia humana
- **Datos Energéticos**: Consumo real vs esperado
- **Datos Geográficos**: Especificaciones por campus

### **Clasificación Automática**
- **Reglas Determinísticas**: Lógica clara y reproducible
- **Agrupación Inteligente**: Evita spam de notificaciones
- **Priorización por Impacto**: Enfoque en eventos significativos

### **Generación con Sistema Experto**
- **Plantillas Estructuradas**: Formatos consistentes y probados
- **Base de Conocimiento**: Conocimiento específico del dominio energético
- **Tono Ejecutivo**: Comunicación para decisores no técnicos

## 📚 Dependencias del Sistema

### **Librerías Principales**
- **pandas**: Manipulación y análisis de datos
- **numpy**: Operaciones numéricas eficientes
- **langchain-groq**: Integración con motor de procesamiento
- **langchain-core**: Plantillas y procesamiento de texto
- **dotenv**: Gestión de variables de entorno

### **Dependencias Externas**
- **API Key**: Groq para motor de procesamiento de texto
- **Datos de Entrada**: `anomalies_detected.csv` (Fase 2)
- **Configuración**: Variables de entorno para el motor

## 🎯 Impacto y Beneficios para la Gestión Universitaria

### **Toma de Decisiones Informada**
- **Claridad Ejecutiva**: Recomendaciones comprensibles para directivos
- **Impacto Económico**: Cuantificación clara del costo de inacción
- **Priorización**: Enfoque en problemas de mayor impacto

### **Acciones Inmediatas**
- **Pasos Concretos**: Instrucciones paso a paso para mantenimiento
- **Soluciones Rápidas**: "Quick Wins" con retorno inmediato
- **Estrategias Sostenibles**: Planificación a largo plazo

### **Comunicación Efectiva**
- **Lenguaje Apropiado**: Sin jerga técnica innecesaria
- **Contexto Relevante**: Información específica por campus y sector
- **Formato Estandarizado**: Tarjetas consistentes para fácil consumo

## 🔧 Especificaciones Técnicas

### **Configuración del Motor**
- **Procesamiento**: Motor de generación eficiente con Groq
- **Modelos**: Optimizados para respuestas consistentes
- **Longitud Máxima**: Textos optimizados para respuestas concisas
- **Manejo de Carga**: Gestión eficiente de peticiones

### **Procesamiento de Datos**
- **Entrada**: CSV con anomalías detectadas (1,313 eventos)
- **Procesamiento**: Clasificación y agrupación inteligente
- **Salida**: Múltiples formatos (CSV, Markdown)

### **Rendimiento**
- **Procesamiento Batch**: Top 5 eventos para demostración
- **Escalabilidad**: Arquitectura preparada para procesamiento completo
- **Caching**: Almacenamiento de recomendaciones generadas

## 📈 Métricas de Evaluación

### **Calidad de Recomendaciones**
- **Claridad**: Comprensibilidad para audiencia no técnica
- **Accesibilidad**: Pasos concretos y realizables
- **Impacto**: Potencial de ahorro económico cuantificado

### **Rendimiento del Sistema**
- **Velocidad**: Tiempo de generación de recomendaciones
- **Confiabilidad**: Respaldo robusto para servicios externos
- **Escalabilidad**: Capacidad de procesamiento creciente

## 🚧 Mejoras Continuas

### **Evolución del Sistema**
- **Versión Original**: PLAN_PHASE_3.md
- **Versión Mejorada**: PLAN_PHASE_3_IMPROVED.md (enfoque ejecutivo)
- **Iteraciones Futuras**: Optimización basada en feedback

### **Expansión de Conocimiento**
- **Nuevos Sectores**: Incorporación de más tipos de instalaciones
- **Casos de Uso**: Expansión de escenarios de anomalías
- **Integraciones**: Conexión con sistemas de gestión universitaria

## 🤝 Guía de Contribución

### **Mejora de Plantillas**
- **Testing A/B**: Comparación de diferentes enfoques
- **Feedback de Usuarios**: Incorporación de sugerencias de gestores
- **Métricas de Éxito**: Medición de efectividad de recomendaciones

### **Extensión de Funcionalidades**
- **Nuevos Motores**: Integración con motores adicionales
- **Automatización**: Programación de generación periódica
- **Visualización**: Dashboards interactivos de recomendaciones

## 📄 Licencia

Este proyecto es parte de la iniciativa Hackaton-IAMINDS para la optimización de la gestión energética de la UPTC.

## 📞 Contacto y Soporte

Para preguntas sobre la Fase 3 de recomendaciones energéticas:
- **Repositorio del Proyecto**: `/phase-3-recommendations`
- **Planificación Original**: Consultar `docs/PLAN_PHASE_3.md`
- **Planificación Mejorada**: Revisar `docs/PLAN_PHASE_3_IMPROVED.md`
- **Scripts Principales**: Analizar `notebooks/01_recommendation_logic.py` y `notebooks/02_llm_advisor.py`
- **Resultados**: Explorar archivos en `results/`

## 🎯 Impacto Estratégico

### **Transformación de Datos en Decisión**
- **Datos Técnicos → Acciones de Negocio**: Traducción efectiva
- **Anomalías → Oportunidades**: Identificación de mejoras
- **Costos Ocultos → Ahorros Visibles**: Cuantificación clara

### **Empoderamiento de Gestores**
- **Autonomía Decisional**: Herramientas para acción inmediata
- **Conocimiento Especializado**: Acceso a expertise energético
- **Medición de Impacto**: Seguimiento de mejoras implementadas

### **Innovación en Gestión Universitaria**
- **Sistemas Expertos**: Uso práctico de conocimiento especializado en administración
- **Eficiencia Operativa**: Optimización de recursos energéticos
- **Sostenibilidad**: Contribución a objetivos ambientales institucionales

---

**Nota Importante**: Esta fase establece las capacidades de asesoramiento que transforman datos complejos en decisiones accionables. El sistema está diseñado para ser el puente entre la detección técnica y la gestión estratégica, permitiendo que cualquier administrador universitario pueda tomar decisiones informadas sobre eficiencia energética.

**Versión**: 3.5 | **Última Actualización**: 2026 | **Estado**: Mejorado y Validado para Uso Ejecutivo
