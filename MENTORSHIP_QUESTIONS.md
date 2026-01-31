# 🧠 Preguntas Estratégicas para Mentoría - GhostEnergy AI

Este documento organiza preguntas clave para aprovechar al máximo tu sesión de mentoría, divididas por áreas de mejora para el proyecto.

---

## 🚀 1. Arquitectura y MLOps (Llevando el proyecto a Producción)
*Actualmente usamos scripts sueltos y Streamlit local. ¿Cómo lo hacemos robusto?*

*   **Pregunta**: "Actualmente ejecuto el pipeline con scripts secuenciales manuales. ¿Qué herramienta de orquestación ligera recomendarías para automatizar esto (Airflow, Prefect, Dagster) considerando que es un MVP?"
*   **Pregunta**: "Para el despliegue del modelo XGBoost, ¿es mejor mantenerlo embebido en la app de Streamlit (como ahora) o recomendarías exponerlo como una API independiente (FastAPI/Flask) para desacoplar el frontend del backend de ML?"
*   **Pregunta**: "¿Qué estrategia de 'Retrenamiento' recomendarías para este tipo de datos de energía? ¿Debería reentrenar el modelo cada semana con los nuevos datos, o solo cuando detecte 'Drift' (desviación) en las predicciones?"

## 🤖 2. Ciencia de Datos y Modelado (Mejorando la Precisión)
*Actualmente usamos XGBoost Regressor y Isolation Forest.*

*   **Pregunta**: "Estoy usando XGBoost como un modelo de regresión general. Para series temporales de energía, ¿crees que valdría la pena experimentar con modelos específicos como **Prophet** o redes **LSTM**? ¿En qué casos suele ganar XGBoost a estos modelos especializados?"
*   **Pregunta**: "En la detección de anomalías (Fase 2), estoy usando *Isolation Forest* sin etiquetas (no supervisado). ¿Cómo puedo validar realmente si las anomalías detectadas son 'reales' si no tengo un dataset etiquetado de fallas pasadas? ¿Qué técnicas de 'Human-in-the-loop' sugieres?"
*   **Pregunta**: "Para el 'Feature Engineering', he usado transformaciones cíclicas (Seno/Coseno) para las horas. ¿Hay alguna otra variable exógena (clima, calendario académico) que suelas ver que impacte drásticamente en modelos de consumo energético?"

## 🧠 3. IA Generativa y LLMs (El Asistente)
*Actualmente usamos Llama-3 vía Groq con el contexto crudo del dataframe.*

*   **Pregunta**: "Mi chatbot actual le pasa un fragmento del DataFrame al prompt del LLM. A medida que los datos crezcan, esto romperá la ventana de contexto. ¿Recomendarías implementar **RAG (Retrieval Augmented Generation)** sobre los logs de anomalías, o es mejor usar una herramienta de 'Text-to-SQL' (como LangChain SQL Agent) para que la IA consulte la base de datos directamente?"
*   **Pregunta**: "¿Cómo puedo evitar las 'alucinaciones' del modelo cuando da recomendaciones técnicas? (Ej: que no invente mantenimientos que no existen). ¿Sería útil implementar 'Guardrails' o una base de conocimiento curada?"

## 💼 4. Producto e Impacto (Valor de Negocio)
*   **Pregunta**: "He calculado el ahorro potencial basándome en eliminar el 'consumo fantasma'. ¿Qué otras métricas de KPI suelen valorar más los Gerentes de Edificios (Facility Managers)? ¿Confort térmico vs. Ahorro?"
*   **Pregunta**: "¿Cómo presentarías este proyecto a un inversor o directivo para demostrar el ROI (Retorno de Inversión) más allá de la simple reducción de la factura de luz?"

---

### 💡 Tips para la sesión:
1.  **Muestra el Dashboard primero**: Deja que el mentor "vea" el producto antes de entrar en código.
2.  **Sé honesto con las limitaciones**: "Sabemos que el modelo no predice bien los feriados atípicos, ¿cómo atacarías eso?".
3.  **Enfócate en el "Siguiente Nivel"**: Ya tienes un MVP funcional, pregunta cómo escalarlo.
