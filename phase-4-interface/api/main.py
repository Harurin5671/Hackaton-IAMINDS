from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import asyncio
import os
import logging
from dotenv import load_dotenv

# Config
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "../../phase-1-exploration/data")
PHASE2_RES = os.path.join(BASE_DIR, "../../phase-2-anomalies/results")
PHASE3_RES = os.path.join(BASE_DIR, "../../phase-3-recommendations/results")
MODEL_PLOTS_DIR = os.path.join(BASE_DIR, "../../phase-1-exploration/docs/model_plots")

# --- App Setup ---
app = FastAPI(title="GhostEnergy AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Data Loading ---
def load_all_data():
    logger.info("Loading data...")
    try:
        df_clean = pd.read_csv(os.path.join(DATA_DIR, "consumos_uptc_clean.csv"))
        df_clean['timestamp'] = pd.to_datetime(df_clean['timestamp'])
    except Exception as e:
        logger.error(f"Error loading clean data: {e}")
        df_clean = pd.DataFrame(columns=['timestamp', 'sede', 'energia_total_kwh'])

    try:
        df_anom = pd.read_csv(os.path.join(PHASE2_RES, "anomalies_detected.csv"))
        df_anom['timestamp'] = pd.to_datetime(df_anom['timestamp'])
    except:
        df_anom = df_clean.copy()

    try:
        df_recs = pd.read_csv(os.path.join(PHASE3_RES, "prioritized_recommendations.csv"))
    except:
        df_recs = pd.DataFrame()

    try:
        df_metrics = pd.read_csv(os.path.join(MODEL_PLOTS_DIR, "metrics.csv"))
    except:
        df_metrics = pd.DataFrame()

    try:
        df_forecast = pd.read_csv(os.path.join(MODEL_PLOTS_DIR, "forecast_2026_full.csv"))
        df_forecast['timestamp'] = pd.to_datetime(df_forecast['timestamp'])
    except:
        df_forecast = pd.DataFrame()
    
    return df_clean, df_anom, df_recs, df_metrics, df_forecast

df_clean, df_anom, df_recs, df_metrics, df_forecast = load_all_data()

# --- Models ---
class ChatRequest(BaseModel):
    sede: str
    pregunta: str

# --- Agent Factory ---
def get_agent_response(sede: str, question: str):
    """
    Creates a Pandas Agent with optimized instructions and robust error handling.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "⚠️ Error: API Key no configurada en el servidor."

    # Heuristic: If simple greeting, skip agent to save tokens/time
    greetings = ["hola", "buenos dias", "buenas tardes", "buenas noches", "hi", "hello"]
    if any(g in question.lower().strip() for g in greetings) and len(question) < 50:
        return f"¡Hola! Soy GhostEnergy AI. Estoy analizando los datos de la sede {sede}. ¿En qué te puedo ayudar hoy?"

    # Context Data
    agent_df = df_anom[df_anom['sede'] == sede].tail(500).reset_index(drop=True)
    
    if agent_df.empty:
        return "No tengo datos cargados para esta sede."

    try:
        from langchain_groq import ChatGroq
        from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
        
        # Use 70b for better reasoning (avoids loops)
        llm = ChatGroq(
            temperature=0.1, 
            groq_api_key=api_key, 
            model_name="llama-3.3-70b-versatile",
            max_retries=2
        )
        
        # Custom Instructions to prevent "thinking" loops and fix parsing
        prefix_prompt = """
        You are an expert Energy Analyst Assistant. 
        You have a pandas DataFrame 'df' with energy consumption anomalies.
        
        CRITICAL RULES FOR REASONING (ReAct Pattern):
        1. You MUST use English keywords for the reasoning steps: 'Thought:', 'Action:', 'Action Input:'.
        2. DO NOT translate these keywords to Spanish (e.g., do NOT use 'Pensamiento:', 'Acción:').
        3. The 'Final Answer:' MUST be in Spanish.
        
        Example of correct behavior:
        Thought: I need to sum the column 'energia_total_kwh'.
        Action: python_repl_ast
        Action Input: df['energia_total_kwh'].sum()
        Observation: 500.5
        Thought: I have the result.
        Final Answer: El consumo total es 500.5 kWh.
        
        GENERAL RULES:
        1. If the user greets, just reply "Final Answer: ¡Hola!..." without tools.
        2. Never invent data.
        """
        
        # Create Agent
        agent = create_pandas_dataframe_agent(
            llm, 
            agent_df, 
            verbose=True, 
            allow_dangerous_code=True,
            prefix=prefix_prompt,
            agent_executor_kwargs={"handle_parsing_errors": True}
        )
        
        # Run with Retry Logic (Exponential Backoff)
        import time
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                response = agent.invoke({"input": question})
                return response['output']
            except Exception as e:
                err_msg = str(e).lower()
                if "429" in err_msg or "rate limit" in err_msg:
                    if attempt < max_retries - 1:
                        wait_time = (attempt + 1) * 2  # 2s, 4s, 6s...
                        logger.warning(f"Groq Rate Limit. Retrying in {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                    else:
                        return "⏳ El sistema está saturado (Groq Rate Limit). Intenta de nuevo en 1 minuto."
                else:
                    raise e # Re-raise other errors

    except Exception as e:
        error_msg = str(e).lower()
        if "429" in error_msg or "rate limit" in error_msg:
            logger.error(f"❌ Still rate limited, using offline mode")
        else:
            logger.error(f"❌ Groq error: {str(e)}")
        
        # Fallback to offline
        agent_df = df_anom[df_anom['sede'] == sede].tail(200)
        return offline_assistant_answer(question, sede, agent_df, df_recs)

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
# def load_all_data():
#     df_clean = pd.read_csv(os.path.join(DATA_DIR, "consumos_uptc_clean.csv"))
#     df_clean['timestamp'] = pd.to_datetime(df_clean['timestamp'])

#     try:
#         df_anom = pd.read_csv(os.path.join(PHASE2_RES, "anomalies_detected.csv"))
#         df_anom['timestamp'] = pd.to_datetime(df_anom['timestamp'])
#     except:
#         df_anom = df_clean.copy()

#     try:
#         df_recs = pd.read_csv(os.path.join(PHASE3_RES, "prioritized_recommendations.csv"))
#     except:
#         df_recs = pd.DataFrame()

#     try:
#         df_metrics = pd.read_csv(os.path.join(MODEL_PLOTS_DIR, "metrics.csv"))
#     except:
#         df_metrics = pd.DataFrame()

#     try:
#         df_forecast = pd.read_csv(os.path.join(MODEL_PLOTS_DIR, "forecast_2026_full.csv"))
#         df_forecast['timestamp'] = pd.to_datetime(df_forecast['timestamp'])
#     except:
#         df_forecast = pd.DataFrame()

#     return df_clean, df_anom, df_recs, df_metrics, df_forecast

# df_clean, df_anom, df_recs, df_metrics, df_forecast = load_all_data()

# --- Modelos Pydantic ---
# class ChatRequest(BaseModel):
#     sede: str
#     pregunta: str

# --- Endpoints ---

@app.get("/")
def root():
    return {"message": "GhostEnergy API Online", "version": "1.0"}

@app.get("/api/sedes")
def get_sedes():
    sedes = df_clean['sede'].unique().tolist() if not df_clean.empty else []
    return {"sedes": sedes}

@app.get("/api/kpis/{sede}")
def get_kpis(sede: str):
    df_view = df_clean[df_clean['sede'] == sede]
    anom_view = df_anom[df_anom['sede'] == sede]
    
    if df_view.empty:
        return {"total_kwh": 0, "anomalías_criticas": 0, "eficiencia": 0, "meta_eficiencia": 95}

    curr_month = df_view['timestamp'].dt.to_period('M').max()
    monthly_data = df_view[df_view['timestamp'].dt.to_period('M') == curr_month]
    
    total_kwh = monthly_data['energia_total_kwh'].sum()
    anom_count = anom_view[anom_view['anomaly_critical'] == 1].shape[0] if 'anomaly_critical' in anom_view.columns else 0
    
    # Get ML Accuracy from metrics if available
    eficiencia = 92 # Fallback
    if not df_metrics.empty:
        m = df_metrics[df_metrics['sede'] == sede]
        if not m.empty:
            eficiencia = float(m.iloc[0]['accuracy_pct'])

    return {
        "total_kwh": total_kwh,
        "anomalías_criticas": anom_count,
        "eficiencia": 92, # Static for MVP
        "meta_eficiencia": 95
    }

@app.get("/api/ml/metrics/{sede}")
def get_ml_metrics(sede: str):
    """
    Retorna las métricas de precisión del modelo ML para una sede.
    """
    if df_metrics.empty:
        return {"sede": sede, "accuracy_pct": 0, "r2": 0, "mae": 0, "rmse": 0}
    
    m = df_metrics[df_metrics['sede'] == sede]
    if m.empty:
        return {"sede": sede, "accuracy_pct": 0, "r2": 0, "mae": 0, "rmse": 0}
    
    return m.iloc[0].to_dict()

@app.get("/api/ml/forecast/{sede}")
def get_ml_forecast(sede: str):
    """
    Retorna el pronóstico mensual de consumo para 2026.
    """
    if df_forecast.empty:
        return {"message": "No forecast data", "data": []}
    
    # Filter by sede
    sede_forecast = df_forecast[df_forecast['sede'] == sede].copy()
    if sede_forecast.empty:
        return {"message": f"No forecast for {sede}", "data": []}
        
    # Aggregate by Month
    monthly = sede_forecast.groupby(pd.Grouper(key='timestamp', freq='ME'))['pred_energy_kwh'].sum().reset_index()
    monthly['month_name'] = monthly['timestamp'].dt.strftime('%b') # Jan, Feb...
    monthly['month_num'] = monthly['timestamp'].dt.month
    
    # Format for chart (list of dicts)
    chart_data = monthly[['month_name', 'pred_energy_kwh']].to_dict(orient='records')
    
    return {"message": "ok", "data": chart_data}

@app.get("/api/consumo-diario/{sede}")
def get_daily(sede: str):
    df_view = df_clean[df_clean['sede'] == sede]
    if df_view.empty: return []
    
    daily = df_view.groupby(pd.Grouper(key='timestamp', freq='D'))['energia_total_kwh'].sum().reset_index()
    daily['timestamp'] = daily['timestamp'].dt.strftime('%Y-%m-%d')
    return daily.to_dict(orient="records")

@app.get("/api/consumo-sector/{sede}")
def get_sector(sede: str):
    df_view = df_clean[df_clean['sede'] == sede]
    if df_view.empty: return []
    
    sector_cols = [c for c in df_view.columns if 'energia_' in c and 'total' not in c]
    melted = df_view.melt(id_vars=['timestamp'], value_vars=sector_cols, var_name='sector', value_name='kWh')
    melted['sector'] = melted['sector'].str.replace('energia_', '').str.replace('_kwh', '')
    
    # Aggregate by sector (Sum)
    grouped = melted.groupby('sector')['kWh'].sum().reset_index()
    return grouped.to_dict(orient="records")

@app.get("/api/anomalias/{sede}")
def get_anomalias(sede: str):
    df_view = df_anom[df_anom['sede'] == sede].copy()
    if df_view.empty: return {"data": []}
    
    # Sort & Format
    df_view['timestamp'] = pd.to_datetime(df_view['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
    df_view = df_view.sort_values('timestamp', ascending=False)
    
    # Select cols
    cols = ['timestamp', 'energia_total_kwh', 'ocupacion_pct', 'anomaly_critical', 'sede']
    out = df_view[[c for c in cols if c in df_view.columns]].to_dict(orient="records")
    return {"data": out}

@app.get("/api/recomendaciones/{sede}")
def get_recs(sede: str):
    if df_recs.empty: return {"data": []}
    
    if 'sede' in df_recs.columns:
        df_view = df_recs[df_recs['sede'] == sede]
    else:
        df_view = df_recs
    
    if df_view.empty:
        return {"message": f"No hay recomendaciones para la sede {sede}", "data": []}
    
    # Convertir a dict manteniendo todas las columnas importantes
    # Columnas esperadas: event_id, category, duration_hours, avg_occupancy, total_kwh, sede
    return {
        "message": "ok",
        "data": df_view.to_dict(orient="records")
    }

# @app.post("/api/chat")
# async def chat_groq(request: ChatRequest):
#     logger.info("=" * 60)
#     logger.info(f"💬 CHAT REQUEST: sede='{request.sede}', pregunta='{request.pregunta}'")
#     logger.info("=" * 60)
    
#     # Create request data for queue
#     request_data = {
#         'sede': request.sede,
#         'pregunta': request.pregunta,
#         'completed': False,
#         'result': None,
#         'request_id': f"{request.sede}_{hash(request.pregunta)}"
#     }
    
#     # Add to queue
#     await chat_queue.put(request_data)
#     logger.info(f" Request added to queue for {request.sede}")
    
#     # Wait for processing to complete
#     max_wait_time = 120  # 2 minutes max wait
#     wait_interval = 0.5
#     elapsed_time = 0
    
#     while not request_data['completed'] and elapsed_time < max_wait_time:
#         await asyncio.sleep(wait_interval)
#         elapsed_time += wait_interval
        
#     return {"data": df_view.to_dict(orient="records")}

# --- Chat Endpoint (The Fix) ---
@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    """
    Uses LangChain Agent to answer naturally.
    """
    logger.info(f"Chat Request for {req.sede}: {req.pregunta}")
    
    response_text = get_agent_response(req.sede, req.pregunta)
    
    return {"respuesta": response_text}