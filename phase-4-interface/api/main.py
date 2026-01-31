# from fastapi import FastAPI, Query, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# import pandas as pd
# import os
# from dotenv import load_dotenv
# from langchain_groq import ChatGroq
# from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent

# # --- Config ---
# load_dotenv()
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# DATA_DIR = os.path.join(BASE_DIR, "../../phase-1-exploration/data")
# PHASE2_RES = os.path.join(BASE_DIR, "../../phase-2-anomalies/results")
# PHASE3_RES = os.path.join(BASE_DIR, "../../phase-3-recommendations/results")

# app = FastAPI(title="GhostEnergy AI API")

# # CORS (para front)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"], 
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # --- Load Data ---
# def load_all_data():
#     df_clean = pd.read_csv(os.path.join(DATA_DIR, "consumos_uptc_clean.csv"))
#     df_clean['timestamp'] = pd.to_datetime(df_clean['timestamp'])

#     try:
#         df_anom = pd.read_csv(os.path.join(PHASE2_RES, "anomalies_detected.csv"))
#         df_anom['timestamp'] = pd.to_datetime(df_anom['timestamp'])
#     except:
#         df_anom = df_clean.copy()

#     try:
#         df_recs = pd.read_csv(os.path.join(BASE_DIR, "../../phase-3-recommendations/results/prioritized_recommendations.csv"))
#     except:
#         df_recs = pd.DataFrame()

#     return df_clean, df_anom, df_recs

# df_clean, df_anom, df_recs = load_all_data()

# # --- Modelos Pydantic ---
# class ChatRequest(BaseModel):
#     sede: str
#     pregunta: str

# # --- Endpoints ---

# @app.get("/")
# def root():
#     return {"message": "👻 GhostEnergy API funcionando!", "status": "online"}

# @app.get("/api/sedes")
# def get_sedes():
#     if df_clean is None:
#         return {"sedes": []}
#     return {"sedes": df_clean['sede'].unique().tolist()}

# @app.get("/api/kpis/{sede}")
# def get_kpis(sede: str):
#     df_view = df_clean[df_clean['sede'] == sede]
#     anom_view = df_anom[df_anom['sede'] == sede]

#     curr_month = df_view['timestamp'].dt.to_period('M').max()
#     monthly_data = df_view[df_view['timestamp'].dt.to_period('M') == curr_month]
#     total_kwh = monthly_data['energia_total_kwh'].sum()
#     anom_count = anom_view[anom_view['anomaly_critical'] == 1].shape[0] if 'anomaly_critical' in anom_view.columns else 0
#     eficiencia = 92

#     return {
#         "total_kwh": total_kwh,
#         "anomalías_criticas": anom_count,
#         "eficiencia": eficiencia,
#         "meta_eficiencia": 95
#     }

# @app.get("/api/consumo-diario/{sede}")
# def consumo_diario(sede: str):
#     df_view = df_clean[df_clean['sede'] == sede]
#     daily = df_view.groupby(pd.Grouper(key='timestamp', freq='D'))['energia_total_kwh'].sum().reset_index()
#     daily['timestamp'] = daily['timestamp'].dt.strftime('%Y-%m-%d')
#     return daily.to_dict(orient="records")

# @app.get("/api/consumo-sector/{sede}")
# def consumo_sector(sede: str):
#     df_view = df_clean[df_clean['sede'] == sede]
#     sector_cols = [c for c in df_view.columns if 'energia_' in c and 'total' not in c]
#     melted = df_view.melt(id_vars=['timestamp'], value_vars=sector_cols, var_name='sector', value_name='kWh')
#     melted['sector'] = melted['sector'].str.replace('energia_', '').str.replace('_kwh', '')
#     return melted.to_dict(orient="records")

# @app.get("/api/anomalias/{sede}")
# def get_anomalias(sede: str):
#     # Filtro seguro por sede
#     df_view = df_anom[df_anom['sede'].str.strip().str.lower() == sede.strip().lower()]
    
#     if df_view.empty:
#         return {"message": f"No se encontraron anomalías para la sede {sede}", "data": []}

#     # Solo seleccionar columnas relevantes
#     cols = ['timestamp', 'energia_total_kwh', 'ocupacion_pct', 'anomaly_critical', 'sede']
#     df_view = df_view[[c for c in cols if c in df_view.columns]].copy()

#     # Formatear timestamp
#     df_view['timestamp'] = pd.to_datetime(df_view['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
    
#     # Ordenar por timestamp descendente (igual que en Streamlit)
#     df_view = df_view.sort_values('timestamp', ascending=False)
    
#     return {"message": "ok", "data": df_view.to_dict(orient="records")}


# @app.get("/api/recomendaciones/{sede}")
# def get_recs(sede: str, top: int = 5):
#     df_view = df_recs[df_recs['sede'].str.strip().str.lower() == sede.strip().lower()]
#     if df_view.empty:
#         return {"message": f"No hay recomendaciones para {sede}", "data": []}

#     df_view = df_view.sort_values('total_kwh', ascending=False).head(top)
#     return {"message": "ok", "data": df_view.to_dict(orient="records")}


# @app.post("/api/chat")
# def chat_groq(request: ChatRequest):
#     # Tomamos solo las últimas 500 filas de anomalías para no saturar tokens
#     agent_df = df_anom[df_anom['sede'] == request.sede].tail(500)[['timestamp','energia_total_kwh','sede','ocupacion_pct','anomaly_critical']]

#     api_key = os.getenv("GROQ_API_KEY")
#     if not api_key:
#         return {"error": "GROQ_API_KEY no configurada"}

#     try:
#         llm = ChatGroq(temperature=0, groq_api_key=api_key, model_name="llama-3.3-70b-versatile")
#         agent = create_pandas_dataframe_agent(llm, agent_df, verbose=False, allow_dangerous_code=True)
#         response = agent.invoke({"input": request.pregunta})
#         return {"respuesta": response['output']}
#     except Exception as e:
#         return {"error": f"Error en el agente: {str(e)}"}


from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent

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
def chat_groq(request: ChatRequest):
    """
    Asistente IA con LangChain Agent.
    Igual que en Streamlit: usa las últimas 500 filas de anomalías.
    """
    # Tomamos solo las últimas 500 filas de anomalías para no saturar tokens
    agent_df = df_anom[df_anom['sede'] == request.sede].tail(500)[['timestamp','energia_total_kwh','sede','ocupacion_pct','anomaly_critical']]

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return {"error": "GROQ_API_KEY no configurada"}

    try:
        llm = ChatGroq(temperature=0, groq_api_key=api_key, model_name="llama-3.3-70b-versatile")
        agent = create_pandas_dataframe_agent(llm, agent_df, verbose=False, allow_dangerous_code=True)
        response = agent.invoke({"input": request.pregunta})
        return {"respuesta": response['output']}
    except Exception as e:
        return {"error": f"Error en el agente: {str(e)}"}