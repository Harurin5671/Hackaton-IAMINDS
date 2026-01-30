# 🛡️ Ficha de Ética y Transparencia (Model Card)

**Proyecto:** GhostEnergy AI - Sistema de Optimización Energética UPTC  
**Versión:** 1.0  
**Fecha:** Enero 2026

---

## 1. Propósito del Modelo
Este sistema tiene como objetivo identificar ineficiencias operativas y predecir el consumo energético en los campus de la UPTC para reducir la huella de carbono y los costos operativos.

## 2. Descripción de los Datos
*   **Fuente**: Datos sintéticos basados en patrones históricos (2018-2025) de la UPTC.
*   **Variables Sensibles**: El modelo utiliza niveles de ocupación de las sedes. Estos datos son **agregados y anonimizados** (porcentaje total por edificio), garantizando que no se rastrean individuos específicos.

## 3. Limitaciones y Riesgos
*   **Naturaleza Sintética**: Al ser entrenado con datos sintéticos, el modelo puede no capturar fallas eléctricas reales o comportamientos humanos impredecibles no simulados.
*   **Falsos Positivos**: El sistema de anomalías puede alertar sobre eventos legítimos (ej: un evento nocturno autorizado). **Siempre se requiere validación humana antes de cortar el suministro.**
*   **Sesgo Estacional**: El modelo puede tener menor precisión durante periodos de vacaciones atípicos (pandemia, paros).

## 4. Explicabilidad (XAI)
Utilizamos valores **SHAP** para garantizar que las decisiones del modelo sean auditables.
*   **Factor Principal**: La ocupación es el predictor más fuerte, seguido de la hora del día.
*   **Transparencia**: El dashboard incluye un panel de "Por qué se generó esta alerta" para cada recomendación.

## 5. Impacto Ambiental
El cálculo de reducción de CO2 utiliza el factor de emisión promedio de la red colombiana (0.164 kg/kWh). Este valor es una estimación y puede variar según la mezcla energética diaria.

---
*Hackathon IAMinds 2026 - Equipo NeuronalCoders*
