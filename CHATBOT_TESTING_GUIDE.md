# 🤖 Guía de Pruebas del Chatbot - GhostEnergy AI

Usa estas preguntas para probar la inteligencia y capacidad de análisis de tu Asistente Energético.

---

## 🟢 Nivel 1: Consultas Básicas (Datos Crudos)
*Prueba si la IA puede leer el DataFrame correctamente.*

1.  "¿Cuál fue el consumo total de energía el último mes?"
2.  "¿Qué día tuvo el pico más alto de consumo y de cuánto fue?"
3.  "¿Cuál es el promedio de ocupación de las aulas?"
4.  "Muéstrame el consumo total dividido por sectores (cocina, aulas, etc)."
5.  "¿Cuántos registros de anomalías críticas hay en total?"

---

## 🟡 Nivel 2: Análisis Temporal (Tendencias)
*Prueba si la IA entiende fechas y patrones.*

1.  "¿Cómo se compara el consumo de los Lunes vs los Domingos?"
2.  "Dime el consumo total de la primera semana de Octubre."
3.  "¿A qué hora del día suele darse el mayor consumo de energía?"
4.  "¿Hubo consumo de energía durante los fines de semana? Si es así, ¿cuánto?"

---

## 🔴 Nivel 3: Diagnóstico y Anomalías (Inteligencia)
*Prueba si el agente puede cruzar datos de anomalías con consumo.*

1.  "Analiza las anomalías detectadas: ¿cuál es la causa más probable?"
2.  "¿Hay alguna relación entre la ocupación baja y el consumo alto?" (Esta es clave para detectar "Consumo Fantasma").
3.  "¿Qué sector es el más ineficiente en términos de consumo vs ocupación?"
4.  "¿Cuánta energía se desperdició en total durante las anomalías críticas?"

---

## 🟣 Nivel 4: Recomendaciones Estratégicas (Rol de Consultor)
*Prueba la capacidad de generar insights de negocio.*

1.  "Basado en los datos, ¿qué tres acciones me recomiendas para ahorrar dinero?"
2.  "Si reduzco el consumo fantasma un 10%, ¿cuánta energía ahorraría al mes?"
3.  "Redacta un breve correo para el rector explicando por qué debemos revisar los aires acondicionados."
4.  "Calcula el costo aproximado del desperdicio de energía asumiendo 800 COP por kWh."

---

## 🧪 Pruebas de "Romper" el Chatbot (Edge Cases)
1.  "Hola, ¿quién eres?" (Debería responder rápido sin usar herramientas).
2.  "Cuéntame un chiste." (Debería responder que solo sabe de energía o intentar hacerlo, pero sin fallar).
3.  "¿Cuál es el consumo en el año 2030?" (Debería decir que no tiene datos para esa fecha).
