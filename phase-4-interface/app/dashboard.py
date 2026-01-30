import streamlit as st
import pandas as pd
import plotly.express as px
import os
import sys
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent

# Config
st.set_page_config(page_title="GhostEnergy AI", page_icon="👻", layout="wide")
load_dotenv()

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "../../phase-1-exploration/data")
PHASE2_RES = os.path.join(BASE_DIR, "../../phase-2-anomalies/results")
PHASE3_RES = os.path.join(BASE_DIR, "../../phase-3-recommendations/results")

@st.cache_data
def load_all_data():
    # 1. Main Consumption
    df_clean = pd.read_csv(os.path.join(DATA_DIR, "consumos_uptc_clean.csv"))
    df_clean['timestamp'] = pd.to_datetime(df_clean['timestamp'])
    
    # 2. Anomalies
    try:
        df_anom = pd.read_csv(os.path.join(PHASE2_RES, "anomalies_detected.csv"))
        df_anom['timestamp'] = pd.to_datetime(df_anom['timestamp'])
    except:
        df_anom = df_clean.copy() # Fallback
        
    # 3. Recommendations
    try:
        df_recs = pd.read_csv(os.path.join(BASE_DIR, "../../phase-3-recommendations/results/prioritized_recommendations.csv"))
    except:
        df_recs = pd.DataFrame()
        
    return df_clean, df_anom, df_recs

def main():
    st.title("👻 GhostEnergy AI: Control Center")
    st.markdown("### Optimización Energética UPTC (Hackathon IAMinds)")
    
    try:
        df_clean, df_anom, df_recs = load_all_data()
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return

    # --- SIDEBAR ---
    st.sidebar.header("Filtros")
    sede_sel = st.sidebar.selectbox("Sede", df_clean['sede'].unique())
    
    # Filter Data
    df_view = df_clean[df_clean['sede'] == sede_sel]
    anom_view = df_anom[df_anom['sede'] == sede_sel]
    
    # --- KPIs ---
    col1, col2, col3 = st.columns(3)
    
    curr_month = df_view['timestamp'].dt.to_period('M').max()
    monthly_data = df_view[df_view['timestamp'].dt.to_period('M') == curr_month]
    
    total_kwh = monthly_data['energia_total_kwh'].sum()
    anom_count = anom_view[anom_view['anomaly_critical'] == 1].shape[0] if 'anomaly_critical' in anom_view.columns else 0
    
    col1.metric("Consumo Mensual (Actual)", f"{total_kwh:,.0f} kWh")
    col2.metric("Anomalías Detectadas", f"{anom_count}", delta=f"Alertas Criticas")
    col3.metric("Eficiencia Estimada", f"{92}%", "Meta: 95%")
    
    # --- TABS ---
    tab1, tab2, tab3 = st.tabs(["📊 Analítica", "🚨 Alertas & Recomendaciones", "💬 Asistente IA"])
    
    with tab1:
        st.subheader("Tendencias de Consumo")
        # Daily Agg
        daily = df_view.groupby(pd.Grouper(key='timestamp', freq='D'))['energia_total_kwh'].sum().reset_index()
        fig = px.line(daily, x='timestamp', y='energia_total_kwh', title=f"Consumo Diario - {sede_sel}")
        st.plotly_chart(fig, width="stretch")
        
        st.subheader("Distribución por Sector")
        # Melt
        sector_cols = [c for c in df_view.columns if 'energia_' in c and 'total' not in c]
        melted = df_view.melt(id_vars=['timestamp'], value_vars=sector_cols, var_name='Sector', value_name='kWh')
        melted['Sector'] = melted['Sector'].str.replace('energia_', '').str.replace('_kwh', '')
        fig2 = px.box(melted, x='Sector', y='kWh', color='Sector')
        st.plotly_chart(fig2, use_container_width=True)
        
    with tab2:
        st.subheader("Anomalías y Acciones Sugeridas")
        
        c1, c2 = st.columns([2, 1])
        
        with c1:
            st.markdown("**Mapa de Calor de Anomalías**")
            if not anom_view.empty and 'anomaly_critical' in anom_view.columns:
                crit = anom_view[anom_view['anomaly_critical'] == 1]
                fig3 = px.scatter(crit, x='timestamp', y='energia_total_kwh', color='ocupacion_pct',
                                  title="Momentos Críticos (Rojo = Alta Intensidad)", color_continuous_scale='Bluered')
                st.plotly_chart(fig3, use_container_width=True)
            else:
                st.info("No se detectaron anomalías críticas en esta vista.")
                
        with c2:
            st.markdown("**📋 Tickets de Recomendación (Prioridad Alta)**")
            if not df_recs.empty:
                recs_sede = df_recs[df_recs['sede'] == sede_sel].head(5)
                for i, row in recs_sede.iterrows():
                    with st.expander(f"Evento #{row['event_id']} ({row['total_kwh']:.0f} kWh)"):
                        st.write(f"**Categoría:** {row['category']}")
                        st.write(f"**Duración:** {row['duration_hours']} horas")
                        st.write(f"**Ocupación Promedio:** {row['avg_occupancy']:.1f}%")
                        st.button(f"Generar Ticket {row['event_id']}")
            else:
                st.write("Sin recomendaciones pendientes.")

    with tab3:
        st.subheader("Asistente Inteligente (Ops Manager)")
        st.info("Pregunta sobre los datos o pide explicaciones de las anomalías.")
        
        user_q = st.chat_input("Ej: ¿Por qué hubo un pico el domingo en Tunja?")
        
        if user_q:
            st.chat_message("user").write(user_q)
            
            with st.spinner("Analizando datos..."):
                try:
                    # Initialize Agent
                    api_key = os.getenv("GROQ_API_KEY") 
                    if not api_key:
                        st.error("API Key no configurada en .env")
                    else:
                        llm = ChatGroq(temperature=0, groq_api_key=api_key, model_name="llama-3.3-70b-versatile")
                        
                        # We give the agent a SAMPLE of the view data to avoid token overflow
                        # Best usage: Give it the 'anomalies' dataframe + metadata
                        agent_df = anom_view.tail(500)[['timestamp', 'energia_total_kwh', 'sede', 'ocupacion_pct', 'anomaly_critical']]
                        
                        agent = create_pandas_dataframe_agent(llm, agent_df, verbose=True, allow_dangerous_code=True)
                        response = agent.invoke({"input": user_q})
                        
                        st.chat_message("assistant").write(response['output'])
                        
                except Exception as e:
                    st.error(f"Error del agente: {e}")

if __name__ == "__main__":
    main()
