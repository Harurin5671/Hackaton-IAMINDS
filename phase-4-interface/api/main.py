from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import os
import logging
from dotenv import load_dotenv

# Config
# Config
# Explicitly load .env from project root to ensure keys are found
env_path = os.path.join(os.path.dirname(__file__), '../../.env')
load_dotenv(dotenv_path=env_path)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "../../phase-1-exploration/data")
PHASE2_RES = os.path.join(BASE_DIR, "../../phase-2-anomalies/results")
PHASE3_RES = os.path.join(BASE_DIR, "../../phase-3-recommendations/results")

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

    return df_clean, df_anom, df_recs

df_clean, df_anom, df_recs = load_all_data()

# --- Models ---
class ChatRequest(BaseModel):
    sede: str
    pregunta: str

# --- Agent Factory ---
def get_agent_response(sede: str, question: str):
    """
    Creates a Pandas Agent with optimized instructions and robust error handling.
    """
    # Heuristic: If simple greeting, skip agent to save tokens/time
    greetings = ["hola", "buenos dias", "buenas tardes", "buenas noches", "hi", "hello"]
    if any(g in question.lower().strip() for g in greetings) and len(question) < 50:
        return f"¡Hola! Soy GhostEnergy AI. Estoy analizando los datos de la sede {sede}. ¿En qué te puedo ayudar hoy?"

    # Context Data
    agent_df = df_anom[df_anom['sede'] == sede].tail(500).reset_index(drop=True)
    
    if agent_df.empty:
        return "No tengo datos cargados para esta sede."

    # 1. Try OpenAI (Paid & Stable)
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        try:
            from langchain_openai import ChatOpenAI
            llm = ChatOpenAI(
                temperature=0,
                model_name="gpt-4o-mini",
                openai_api_key=openai_key
            )
            logger.info("Using OpenAI (gpt-4o-mini)")
        except ImportError:
            return "⚠️ Error: Falta librería 'langchain-openai'. Ejecuta: pip install langchain-openai"

    # 2. Fallback to Groq (Free & Limited)
    else:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            return "⚠️ Error: No se encontraron API Keys (ni OPENAI_API_KEY ni GROQ_API_KEY)."
        
        from langchain_groq import ChatGroq
        llm = ChatGroq(
            temperature=0.1, 
            groq_api_key=api_key, 
            model_name="llama-3.3-70b-versatile",
            max_retries=2
        )
        logger.info("Using Groq (llama-3.3-70b)")

    try:
        from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
        
        # Custom Instructions (Fixed for ReAct)
        # Custom Instructions (Strict ReAct for GPT-4o-mini)
        prefix_prompt = """
        You are an expert Energy Analyst Assistant using a pandas DataFrame 'df'.
        
        FORMAT INSTRUCTIONS:
        You usually normally output 'Thought:', 'Action:', 'Action Input:', 'Observation:'.
        
        CRITICAL: The ONLY valid value for 'Action:' is 'python_repl_ast'. Never write a sentence there.
        
        Example of CORRECT interaction:
        Thought: I need to check the columns.
        Action: python_repl_ast
        Action Input: df.columns
        Observation: Index(['energy', 'date'], dtype='object')
        Thought: I have the data.
        Final Answer: Las columnas son energy y date.
        
        Example of WRONG interaction (DO NOT DO THIS):
        Action: I will check the columns  <-- WRONG!
        
        RULES:
        1. 'Action:' must ALWAYS be 'python_repl_ast'.
        2. 'Final Answer:' must be in Spanish.
        3. If you just want to talk (greetings), reply directly with "Final Answer: Hola...".
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
                
                # OpenAI Specific
                if "insufficient_quota" in err_msg or ("429" in err_msg and "openai" in err_msg):
                    return "⚠️ Error OpenAI: Cuota insuficiente. Por favor revisa tu crédito en platform.openai.com"
                
                # Groq/Generic Rate Limit
                if "429" in err_msg or "rate limit" in err_msg:
                    if attempt < max_retries - 1:
                        wait_time = (attempt + 1) * 2
                        logger.warning(f"Rate Limit ({'OpenAI' if openai_key else 'Groq'}). Retrying in {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                    else:
                        return "⏳ El sistema está saturado. Por favor intenta de nuevo en 1 minuto."
                
                # Other errors
                logger.error(f"Agent Error: {e}")
                return f"Lo siento, tuve un problema técnico: {str(e)}"

    except Exception as e:
        logger.error(f"Agent Error: {e}")
        return f"Lo siento, tuve un problema técnico: {str(e)}"

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
    
    return {
        "total_kwh": total_kwh,
        "anomalías_criticas": anom_count,
        "eficiencia": 92, # Static for MVP
        "meta_eficiencia": 95
    }

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
        
    return {"data": df_view.to_dict(orient="records")}

# --- Chat Endpoint (The Fix) ---
@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    """
    Uses LangChain Agent to answer naturally.
    """
    logger.info(f"Chat Request for {req.sede}: {req.pregunta}")
    
    response_text = get_agent_response(req.sede, req.pregunta)
    
    return {"respuesta": response_text}