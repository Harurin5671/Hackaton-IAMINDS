# 🧪 Pruebas del Sistema Chat API

## 📋 Estado Actual

### ✅ **Backend Implementado**
- **Endpoint**: `POST /api/chat`
- **Modelo**: `ChatRequest {sede: string, pregunta: string}`
- **Respuesta**: `ChatResponse {respuesta: string | error: string}`
- **IA**: Groq Llama 3.3 70B con LangChain Agent
- **Contexto**: Últimas 500 filas de anomalías de la sede

### ✅ **Frontend Conectado**
- **Servicio**: `DataService.chat()` implementado
- **Componente**: Dashboard con manejo real de API
- **UI**: Chat con loading y manejo de errores

## 🚀 **Cómo Probar**

### **1. Iniciar Backend**
```bash
cd phase-4-interface/api
python3 main.py
```
**Verificar**: API debe correr en http://localhost:8000

### **2. Probar con Script (Recomendado)**
```bash
cd phase-4-interface
python3 test_chat_api.py
```
Este script:
- ✅ Verifica que la API esté corriendo
- ✅ Prueba el endpoint de chat con pregunta de ejemplo
- ✅ Muestra respuesta completa o error detallado

### **3. Probar con Postman/Curl**
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "sede": "Sede Central",
    "pregunta": "¿Cuál es el consumo total y cuántas anomalías críticas hay?"
  }'
```

### **4. Probar con Frontend**
```bash
cd phase-4-interface/angular-app
npm start
```
Luego:
1. Selecciona una sede en el dropdown
2. Escribe una pregunta en el chat
3. Observa la respuesta real de Groq

## 🔑 **Requisitos**

### **Variables de Entorno**
Crear `.env` en `phase-4-interface/api/`:
```env
GROQ_API_KEY=tu_api_key_aqui
```

### **Dependencias Backend**
```bash
cd phase-4-interface/api
pip3 install fastapi uvicorn pandas python-dotenv langchain langchain-groq langchain-experimental
```

## 📊 **Qué Deberías Ver**

### **Respuesta Exitosa**
```json
{
  "respuesta": "Basado en los datos de anomalías de Sede Central, el consumo total es de X kWh y se detectaron Y anomalías críticas..."
}
```

### **Posibles Errores**
- `GROQ_API_KEY no configurada` → Configurar API key
- `No se encontraron anomalías para la sede X` → Probar con otra sede
- `Error en el agente: ...` → Revisar conexión a Groq

## 🐛 **Troubleshooting**

### **API no responde**
1. Verificar que el backend esté corriendo
2. Revisar que el puerto 8000 esté libre
3. Checkear logs del backend

### **Error de Groq API**
1. Verificar API key válida
2. Checkear límites de uso
3. Revisar conexión a internet

### **Frontend no conecta**
1. Verificar CORS en backend (ya configurado)
2. Revisar que backend esté en 8000
3. Checkear consola del navegador

## 🎯 **Test de Integración Completo**

1. **Iniciar ambos servicios**
2. **Probar API con script** → Debe funcionar
3. **Probar frontend** → Debe mostrar respuestas reales
4. **Verificar logs** → Backend debe mostrar llamadas LangChain

Si todo funciona, el chat responderá con análisis real de datos usando Groq! 🎉
