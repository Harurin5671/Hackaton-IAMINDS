from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import os
import logging
import asyncio
import threading
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent

# --- Setup Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Global Queue for Sequential Processing ---
chat_queue = asyncio.Queue()
processing_lock = asyncio.Lock()
is_processing = False

# --- Config ---
load_dotenv()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "../../phase-1-exploration/data")
PHASE2_RES = os.path.join(BASE_DIR, "../../phase-2-anomalies/results")
PHASE3_RES = os.path.join(BASE_DIR, "../../phase-3-recommendations/results")

app = FastAPI(title="GhostEnergy AI API")

# CORS (para front)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    sede: str
    pregunta: str

# --- Load Data ---
def load_all_data():
    df_clean = pd.read_csv(os.path.join(DATA_DIR, "consumos_uptc_clean.csv"))
    df_clean['timestamp'] = pd.to_datetime(df_clean['timestamp'])
    
    try:
        df_anom = pd.read_csv(os.path.join(PHASE2_RES, "anomalies_detected.csv"))
        df_anom['timestamp'] = pd.to_datetime(df_anom['timestamp'])
    except:
        df_anom = df_clean.copy()
        
    try:
        df_recs = pd.read_csv(os.path.join(PHASE3_RES, "prioritized_recommendations.csv"))
    except:
        df_recs = pd.DataFrame()
    
    return df_clean, df_anom, df_recs

df_clean, df_anom, df_recs = load_all_data()

# --- Sequential Groq Processing ---
async def process_groq_request(request_data):
    """Process a single Groq request with all optimizations"""
    try:
        logger.info(f"🔄 Processing queued request for {request_data['sede']}")
        
        # Tomamos solo las últimas 200 filas de anomalías
        agent_df = df_anom[df_anom['sede'] == request_data['sede']].tail(200)
        logger.info(f"📊 Found {len(agent_df)} anomaly records for {request_data['sede']}")
        
        # Check Groq availability
        try:
            from langchain_groq import ChatGroq
            from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
            import tabulate
        except ImportError as e:
            logger.error(f"❌ Groq libraries not available: {e}")
            return {"respuesta": offline_assistant_answer(request_data['pregunta'], request_data['sede'], agent_df, df_recs)}

        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            logger.warning("⚠️  GROQ_API_KEY not found")
            return {"respuesta": offline_assistant_answer(request_data['pregunta'], request_data['sede'], agent_df, df_recs)}

        # Initialize Groq with optimizations
        llm = ChatGroq(
            model="llama-3.1-8b-instant", 
            temperature=0.2, 
            groq_api_key=api_key,
            max_retries=1,  # Minimal retries
            request_timeout=60.0
        )
        
        # Prepare comprehensive data from all sources
        # 1. Anomalies data (current)
        anomaly_data = {
            'total_records': len(agent_df),
            'critical_anomalies': len(agent_df[agent_df['anomaly_critical'] == 1]) if 'anomaly_critical' in agent_df.columns else 0,
            'total_consumption_anomalies': agent_df['energia_total_kwh'].sum() if 'energia_total_kwh' in agent_df.columns else 0,
            'avg_occupancy_anomalies': agent_df['ocupacion_pct'].mean() if 'ocupacion_pct' in agent_df.columns else 0,
            'anomaly_date_range': {
                'start': agent_df['timestamp'].min() if 'timestamp' in agent_df.columns else 'N/A',
                'end': agent_df['timestamp'].max() if 'timestamp' in agent_df.columns else 'N/A'
            }
        }

        # 2. Daily consumption data
        daily_data = df_clean[df_clean['sede'] == request_data['sede']]
        if not daily_data.empty:
            # Get data for the specific month if asked
            if 'enero' in request_data['pregunta'].lower() or 'january' in request_data['pregunta'].lower():
                daily_data = daily_data[daily_data['timestamp'].dt.month == 1]
            
            daily_summary = {
                'total_consumption': daily_data['energia_total_kwh'].sum() if 'energia_total_kwh' in daily_data.columns else 0,
                'avg_daily_consumption': daily_data['energia_total_kwh'].mean() if 'energia_total_kwh' in daily_data.columns else 0,
                'max_daily_consumption': daily_data['energia_total_kwh'].max() if 'energia_total_kwh' in daily_data.columns else 0,
                'min_daily_consumption': daily_data['energia_total_kwh'].min() if 'energia_total_kwh' in daily_data.columns else 0,
                'total_days': len(daily_data),
                'consumption_date_range': {
                    'start': daily_data['timestamp'].min() if 'timestamp' in daily_data.columns else 'N/A',
                    'end': daily_data['timestamp'].max() if 'timestamp' in daily_data.columns else 'N/A'
                }
            }
        else:
            daily_summary = {'error': 'No daily consumption data available'}

        # 3. Sector consumption data
        sector_data = df_clean[df_clean['sede'] == request_data['sede']]
        sector_summary = {}
        if not sector_data.empty:
            sector_cols = [c for c in sector_data.columns if 'energia_' in c and 'total' not in c]
            for col in sector_cols:
                sector_name = col.replace('energia_', '').replace('_kwh', '')
                sector_summary[sector_name] = sector_data[col].sum()

        # 4. Recommendations data
        rec_data = df_recs[df_recs['sede'] == request_data['sede']] if not df_recs.empty else pd.DataFrame()
        if not rec_data.empty:
            recommendations_summary = {
                'total_recommendations': len(rec_data),
                'top_categories': rec_data['category'].value_counts().head(3).to_dict() if 'category' in rec_data.columns else {},
                'total_potential_savings': rec_data['total_kwh'].sum() if 'total_kwh' in rec_data.columns else 0,
                'avg_duration': rec_data['duration_hours'].mean() if 'duration_hours' in rec_data.columns else 0
            }
        else:
            recommendations_summary = {'error': 'No recommendations data available'}

        # 5. KPIs data
        kpi_data = {
            'total_kwh': daily_summary.get('total_consumption', 0),
            'critical_anomalies': anomaly_data['critical_anomalies'],
            'eficiencia': 92,  # This could be calculated
            'meta_eficiencia': 95
        }
        
        # Comprehensive prompt with all data sources
        direct_prompt = f"""
        Analiza estos datos energéticos COMPLETOS para la sede {request_data['sede']}:

        === CONSUMO DIARIO ===
        - Consumo total: {daily_summary.get('total_consumption', 0):.2f} kWh
        - Promedio diario: {daily_summary.get('avg_daily_consumption', 0):.2f} kWh
        - Máximo diario: {daily_summary.get('max_daily_consumption', 0):.2f} kWh
        - Mínimo diario: {daily_summary.get('min_daily_consumption', 0):.2f} kWh
        - Total días analizados: {daily_summary.get('total_days', 0)}
        - Período: {daily_summary.get('consumption_date_range', {}).get('start', 'N/A')} a {daily_summary.get('consumption_date_range', {}).get('end', 'N/A')}

        === ANOMALÍAS DETECTADAS ===
        - Total anomalías: {anomaly_data['total_records']}
        - Anomalías críticas: {anomaly_data['critical_anomalies']}
        - Consumo en anomalías: {anomaly_data['total_consumption_anomalies']:.2f} kWh
        - Ocupación promedio en anomalías: {anomaly_data['avg_occupancy_anomalies']:.1f}%
        - Período anomalías: {anomaly_data['anomaly_date_range']['start']} a {anomaly_data['anomaly_date_range']['end']}

        === CONSUMO POR SECTOR ===
        {chr(10).join([f"- {sector}: {consumption:.2f} kWh" for sector, consumption in sector_summary.items()]) if sector_summary else "- No hay datos por sector disponibles"}

        === RECOMENDACIONES ===
        - Total recomendaciones: {recommendations_summary.get('total_recommendations', 0)}
        - Ahorro potencial: {recommendations_summary.get('total_potential_savings', 0):.2f} kWh
        - Categorías principales: {recommendations_summary.get('top_categories', {})}

        === KPIs ===
        - Consumo total KPI: {kpi_data['total_kwh']:.2f} kWh
        - Anomalías críticas KPI: {kpi_data['critical_anomalies']}
        - Eficiencia: {kpi_data['eficiencia']}%
        - Meta de eficiencia: {kpi_data['meta_eficiencia']}%

        PREGUNTA: {request_data['pregunta']}

        INSTRUCCIONES ESPECÍFICAS:
        1. Usa TODOS los datos proporcionados para responder
        2. Si preguntas sobre consumo mensual específico, usa el consumo total diario
        3. Si preguntas sobre anomalías, usa el conteo de anomalías críticas
        4. Si preguntas sobre sectores, muestra los consumos por sector
        5. Si preguntas sobre recomendaciones, menciona el ahorro potencial
        6. Sé específico y cuantitativo con los datos
        7. Responde en español
        8. Proporciona insights basados en los múltiples conjuntos de datos
        """
        
        logger.info("📨 Sending SINGLE direct request to Groq...")
        response = await llm.ainvoke(direct_prompt)
        
        output = response.content if hasattr(response, 'content') else str(response)
        logger.info(f"✅ GROQ SUCCESS: {output[:100]}{'...' if len(output) > 100 else ''}")
        
        return {"respuesta": output}
        
    except Exception as e:
        error_msg = str(e).lower()
        if "429" in error_msg or "rate limit" in error_msg:
            logger.error(f"❌ Still rate limited, using offline mode")
        else:
            logger.error(f"❌ Groq error: {str(e)}")
        
        # Fallback to offline
        agent_df = df_anom[df_anom['sede'] == request_data['sede']].tail(200)
        return {"respuesta": offline_assistant_answer(request_data['pregunta'], request_data['sede'], agent_df, df_recs)}

async def queue_worker():
    """Background worker that processes chat requests sequentially"""
    global is_processing
    
    while True:
        try:
            # Wait for a request
            request_data = await chat_queue.get()
            
            async with processing_lock:
                is_processing = True
                logger.info(f"🎯 Started processing request for {request_data['sede']}")
                
                # Process the request
                result = await process_groq_request(request_data)
                
                # Store result for the original request to retrieve
                request_data['result'] = result
                request_data['completed'] = True
                
                logger.info(f"✅ Completed request for {request_data['sede']}")
                is_processing = False
                
            chat_queue.task_done()
            
        except Exception as e:
            logger.error(f"❌ Queue worker error: {str(e)}")
            is_processing = False
            chat_queue.task_done()
        
        # Small delay between requests to be extra safe
        await asyncio.sleep(1)

# Start the queue worker when app starts
@app.on_event("startup")
async def startup_event():
    """Start the background queue worker"""
    asyncio.create_task(queue_worker())
    logger.info("🚀 Chat queue worker started")

# --- Offline assistant igual que en Streamlit ---
def offline_assistant_answer(user_question: str, sede: str, anom_df, recs_df) -> str:
    logger.info(f"🤖 OFFLINE MODE: Processing question for sede '{sede}': '{user_question}'")
    
    q = (user_question or "").lower().strip()
    logger.info(f"🔍 Question keywords: {q}")

    # Recomendaciones top 3
    sede_recs = recs_df[recs_df["sede"] == sede] if not recs_df.empty else pd.DataFrame()
    sede_recs = sede_recs.sort_values("total_kwh", ascending=False).head(3) if not sede_recs.empty else sede_recs
    logger.info(f"📋 Found {len(sede_recs)} recommendations for {sede}")

    # Últimas anomalías críticas
    sede_anom = anom_df[anom_df["sede"] == sede] if "sede" in anom_df.columns else anom_df.copy()
    if "anomaly_critical" in sede_anom.columns:
        sede_anom = sede_anom[sede_anom["anomaly_critical"] == 1].copy()
    if "timestamp" in sede_anom.columns:
        sede_anom["timestamp"] = pd.to_datetime(sede_anom["timestamp"], errors="coerce")
        sede_anom = sede_anom.sort_values("timestamp", ascending=False).head(5)
    logger.info(f"🚨 Found {len(sede_anom)} critical anomalies for {sede}")

    # Lógica simple de respuesta
    if any(k in q for k in ["recomend", "acción", "hacer", "suger", "reducir"]):
        logger.info("🎯 Using recommendation logic")
        if sede_recs.empty:
            response = "No hay recomendaciones disponibles para esta sede."
            logger.info("❌ No recommendations found")
            return response
        response = "\n".join([f"- {r['category']} (~{r['total_kwh']:.1f} kWh)" for _, r in sede_recs.iterrows()])
        logger.info(f"✅ Generated recommendation response: {response}")
        return response

    if any(k in q for k in ["anomal", "alert", "pico", "desperd", "waste", "crític"]):
        logger.info("🚨 Using anomaly logic")
        if sede_anom.empty:
            response = "No hay anomalías críticas recientes registradas."
            logger.info("❌ No critical anomalies found")
            return response
        response = "\n".join([f"- {a['timestamp']}: {a.get('energia_total_kwh','NA')} kWh" for _, a in sede_anom.iterrows()])
        logger.info(f"✅ Generated anomaly response: {response}")
        return response

    # Default: resumen rápido
    logger.info("📝 Using default summary logic")
    parts = []
    if not sede_recs.empty:
        r = sede_recs.iloc[0]
        parts.append(f"- Recomendación #1: {r['category']} (~{r['total_kwh']:.1f} kWh)")
    if not sede_anom.empty:
        a = sede_anom.iloc[0]
        parts.append(f"- Última anomalía crítica: {a['timestamp']} ({a['energia_total_kwh']} kWh)")
    
    response = "\n".join(parts) or "No hay datos suficientes para responder."
    logger.info(f"✅ Generated default response: {response}")
    return response

# --- Load Data ---
def load_all_data():
    df_clean = pd.read_csv(os.path.join(DATA_DIR, "consumos_uptc_clean.csv"))
    df_clean['timestamp'] = pd.to_datetime(df_clean['timestamp'])

    try:
        df_anom = pd.read_csv(os.path.join(PHASE2_RES, "anomalies_detected.csv"))
        df_anom['timestamp'] = pd.to_datetime(df_anom['timestamp'])
    except:
        df_anom = df_clean.copy()

    try:
        df_recs = pd.read_csv(os.path.join(PHASE3_RES, "prioritized_recommendations.csv"))
    except:
        df_recs = pd.DataFrame()

    return df_clean, df_anom, df_recs

df_clean, df_anom, df_recs = load_all_data()

# --- Modelos Pydantic ---
class ChatRequest(BaseModel):
    sede: str
    pregunta: str

# --- Endpoints ---

@app.get("/")
def root():
    return {"message": "👻 GhostEnergy API funcionando!", "status": "online"}

@app.get("/api/sedes")
def get_sedes():
    if df_clean is None:
        return {"sedes": []}
    return {"sedes": df_clean['sede'].unique().tolist()}

@app.get("/api/kpis/{sede}")
def get_kpis(sede: str):
    df_view = df_clean[df_clean['sede'] == sede]
    anom_view = df_anom[df_anom['sede'] == sede]

    curr_month = df_view['timestamp'].dt.to_period('M').max()
    monthly_data = df_view[df_view['timestamp'].dt.to_period('M') == curr_month]
    total_kwh = monthly_data['energia_total_kwh'].sum()
    anom_count = anom_view[anom_view['anomaly_critical'] == 1].shape[0] if 'anomaly_critical' in anom_view.columns else 0
    eficiencia = 92

    return {
        "total_kwh": total_kwh,
        "anomalías_criticas": anom_count,
        "eficiencia": eficiencia,
        "meta_eficiencia": 95
    }

@app.get("/api/consumo-diario/{sede}")
def consumo_diario(sede: str):
    df_view = df_clean[df_clean['sede'] == sede]
    daily = df_view.groupby(pd.Grouper(key='timestamp', freq='D'))['energia_total_kwh'].sum().reset_index()
    daily['timestamp'] = daily['timestamp'].dt.strftime('%Y-%m-%d')
    return daily.to_dict(orient="records")

@app.get("/api/consumo-sector/{sede}")
def consumo_sector(sede: str):
    df_view = df_clean[df_clean['sede'] == sede]
    sector_cols = [c for c in df_view.columns if 'energia_' in c and 'total' not in c]
    melted = df_view.melt(id_vars=['timestamp'], value_vars=sector_cols, var_name='sector', value_name='kWh')
    melted['sector'] = melted['sector'].str.replace('energia_', '').str.replace('_kwh', '')
    return melted.to_dict(orient="records")

@app.get("/api/anomalias/{sede}")
def get_anomalias(sede: str):
    """
    Retorna las anomalías detectadas para una sede específica.
    Igual que en Streamlit: filtra por sede, formatea y ordena.
    """
    # Filtro seguro por sede
    df_view = df_anom[df_anom['sede'].str.strip().str.lower() == sede.strip().lower()]
    
    if df_view.empty:
        return {"message": f"No se encontraron anomalías para la sede {sede}", "data": []}

    # Solo seleccionar columnas relevantes
    cols = ['timestamp', 'energia_total_kwh', 'ocupacion_pct', 'anomaly_critical', 'sede']
    df_view = df_view[[c for c in cols if c in df_view.columns]].copy()

    # Formatear timestamp
    df_view['timestamp'] = pd.to_datetime(df_view['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
    
    # Ordenar por timestamp descendente (igual que en Streamlit)
    df_view = df_view.sort_values('timestamp', ascending=False)
    
    return {"message": "ok", "data": df_view.to_dict(orient="records")}

@app.get("/api/recomendaciones/{sede}")
def get_recomendaciones(sede: str):
    """
    Retorna las recomendaciones priorizadas para una sede específica.
    Igual que en Streamlit: filtra por sede y retorna top 5.
    """
    if df_recs.empty:
        return {"message": "No hay recomendaciones disponibles", "data": []}
    
    # Filtrar por sede (si la columna existe)
    if 'sede' in df_recs.columns:
        recs_sede = df_recs[df_recs['sede'] == sede]
    else:
        recs_sede = df_recs
    
    if recs_sede.empty:
        return {"message": f"No hay recomendaciones para la sede {sede}", "data": []}
    
    # Convertir a dict manteniendo todas las columnas importantes
    # Columnas esperadas: event_id, category, duration_hours, avg_occupancy, total_kwh, sede
    return {
        "message": "ok",
        "data": recs_sede.to_dict(orient="records")
    }

@app.post("/api/chat")
async def chat_groq(request: ChatRequest):
    logger.info("=" * 60)
    logger.info(f"💬 CHAT REQUEST: sede='{request.sede}', pregunta='{request.pregunta}'")
    logger.info("=" * 60)
    
    # Create request data for queue
    request_data = {
        'sede': request.sede,
        'pregunta': request.pregunta,
        'completed': False,
        'result': None,
        'request_id': f"{request.sede}_{hash(request.pregunta)}"
    }
    
    # Add to queue
    await chat_queue.put(request_data)
    logger.info(f"� Request added to queue for {request.sede}")
    
    # Wait for processing to complete
    max_wait_time = 120  # 2 minutes max wait
    wait_interval = 0.5
    elapsed_time = 0
    
    while not request_data['completed'] and elapsed_time < max_wait_time:
        await asyncio.sleep(wait_interval)
        elapsed_time += wait_interval
        
        if elapsed_time % 10 < 1:  # Log every 10 seconds
            logger.info(f"⏳ Waiting for response... ({elapsed_time:.1f}s elapsed)")
    
    if request_data['completed']:
        logger.info(f"🎉 Request completed for {request.sede}")
        return request_data['result']
    else:
        logger.error(f"⏰ Timeout waiting for response for {request.sede}")
        # Fallback to offline mode
        agent_df = df_anom[df_anom['sede'] == request.sede].tail(200)
        fallback_response = offline_assistant_answer(request.pregunta, request.sede, agent_df, df_recs)
        return {"respuesta": fallback_response}