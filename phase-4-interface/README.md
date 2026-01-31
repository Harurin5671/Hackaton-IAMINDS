# GhostEnergy AI - Instrucciones de Inicio

## 🚀 Iniciar la Aplicación

### 1. Iniciar el Backend (FastAPI)
```bash
cd phase-4-interface/api
python main.py
```
El backend estará disponible en: http://localhost:8000

### 2. Iniciar el Frontend (Angular)
```bash
cd phase-4-interface/angular-app
npm start
```
El frontend estará disponible en: http://localhost:4200

## 📋 Requisitos Previos

### Backend
- Python 3.8+
- FastAPI
- Pandas
- Python-dotenv
- LangChain
- Groq API key (configurada en .env)

### Frontend  
- Node.js 18+
- Angular 21
- npm

## 🔧 Configuración

1. **Variables de Entorno Backend**:
   - Crear archivo `.env` en `phase-4-interface/api/`
   - Agregar: `GROQ_API_KEY=tu_api_key_aqui`

2. **Dependencias Frontend**:
   ```bash
   cd phase-4-interface/angular-app
   npm install
   ```

## 🌐 Acceso a la Aplicación

- **Dashboard Principal**: http://localhost:4200
- **API Documentation**: http://localhost:8000/docs
- **API Health Check**: http://localhost:8000

## 📊 Funcionalidades

### ✅ Implementadas
- Conexión Angular ↔ FastAPI
- Dashboard con KPIs en tiempo real
- Chat interactivo con asistente IA
- Selección de sedes
- Visualización de datos energéticos
- Detección de anomalías
- Recomendaciones de optimización

### 🔮 Próximamente
- Gráficos interactivos con Chart.js
- Exportación de reportes
- Notificaciones en tiempo real
- Modo oscuro

## 🛠️ Solución de Problemas

### Errores Comunes
1. **CORS**: Asegúrate que el backend tenga CORS configurado para `http://localhost:4200`
2. **API Key**: Verifica que la API key de Groq esté configurada correctamente
3. **Dependencias**: Ejecuta `npm install` si hay errores de módulos faltantes

### Logs y Debugging
- **Backend**: Ver logs en terminal donde se ejecuta `python main.py`
- **Frontend**: Ver consola del navegador (F12) para errores de JavaScript/Angular

## 📞 Soporte

Si encuentras problemas:
1. Revisa que ambos servicios estén corriendo
2. Verifica la conexión a internet
3. Consulta los logs para errores específicos
