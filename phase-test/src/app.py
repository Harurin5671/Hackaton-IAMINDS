import streamlit as st
import pandas as pd
import plotly.express as px
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
import sys



# Load environment variables
load_dotenv()

# Add src to path if needed, though running from root should work if __init__.py exists or we use correct imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from data_generator import generate_uptc_data
    from models import train_predictive_model, detect_anomalies
    from recommendations import analyze_inefficiencies
    from ethics import get_ethics_disclaimer
except ImportError:
    # Fallback for direct execution from src/
    from src.data_generator import generate_uptc_data
    from src.models import train_predictive_model, detect_anomalies
    from src.recommendations import analyze_inefficiencies
    from src.ethics import get_ethics_disclaimer

# --- CONFIG ---
st.set_page_config(page_title="GhostEnergy AI - UPTC", layout="wide", page_icon="👻")
st.markdown('<script>fetch(window.location.href, {{headers: {{"ngrok-skip-browser-warning": "true"}}}});</script>', unsafe_allow_html=True)

# Helper to load data
@st.cache_data
def load_data():
    if not os.path.exists("uptc_final.csv"):
        df = generate_uptc_data()
        df.to_csv("uptc_final.csv")
    else:
        df = pd.read_csv("uptc_final.csv", parse_dates=True, index_col=0)
    
    # Process data with models if not already processed
    if 'pred_consumption' not in df.columns or 'anomaly' not in df.columns:
        model, df = train_predictive_model(df)
        df = detect_anomalies(df)
        df = analyze_inefficiencies(df)
        df.to_csv("uptc_processed.csv")
    
    return df

# --- MAIN APP ---
def main():
    st.title("👻 GhostEnergy AI - IAMinds 2026")
    st.markdown("### Plataforma de Sostenibilidad Operativa Universitaria")
    
    with st.spinner("Cargando y procesando datos..."):
        df = load_data()

    # --- SIDEBAR FILTERS ---
    with st.sidebar:
        st.header("🔍 Configuración")
        st.image("https://cdn-icons-png.flaticon.com/512/3203/3203874.png", width=100)
        
        sede_sel = st.selectbox("Sede", df['sede'].unique())
        all_sectors = df['sector'].unique().tolist()
        sector_sel = st.multiselect("Sectores", all_sectors, default=all_sectors)
        
        st.markdown("---")
        st.markdown(get_ethics_disclaimer())

    # Filter data
    # Ensure index is datetime
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)

    df_view = df[(df['sede'] == sede_sel) & (df['sector'].isin(sector_sel))]

    if df_view.empty:
        st.warning("No hay datos para la selección actual.")
        return

    # --- KPIs ---
    st.subheader("📊 Impacto y Ahorros Proyectados")
    c1, c2, c3 = st.columns(3)
    
    # Calculate "Waste" as positive residuals (consumed > predicted)
    # or purely anomalies. Let's use anomalies for "detected waste"
    anomalies_df = df_view[df_view['anomaly'] == -1]
    potential_waste_kwh = anomalies_df['consumption'].sum() * 0.2 # Assume we can save 20% of anomalous consumption
    
    # Or use residual if positive
    waste_residual = df_view[df_view['residual'] > 0]['residual'].sum()
    
    # Let's be conservative and use waste_residual
    total_savings_kwh = waste_residual
    
    c1.metric("Ahorro Potencial (kWh)", f"{total_savings_kwh:,.0f}", delta="Estimado IA")
    c2.metric("CO2 Evitado (kg)", f"{total_savings_kwh * 0.164:,.1f}", delta="Reducción")
    c3.metric("Ahorro Económico (COP)", f"${total_savings_kwh * 900:,.0f}", delta="Aprox.")

    # --- TABS ---
    tab1, tab2, tab3 = st.tabs(["📉 Análisis de Consumo", "🚨 Ineficiencias y Recomendaciones", "🤖 Asistente XAI"])

    with tab1:
        st.subheader(f"Tendencia de Consumo: {sede_sel}")
        # Resample for clearer chart if too much data, e.g., daily mean
        df_daily = df_view.resample('D')['consumption'].sum().reset_index()
        fig = px.line(df_daily, x='index', y='consumption', title="Consumo Diario (kWh)", template="plotly_dark")
        st.plotly_chart(fig, key="chart1")
        
        st.markdown("**Comparativa por Sector**")
        fig2 = px.box(df_view, x='sector', y='consumption', color='sector', points="outliers")
        st.plotly_chart(fig2, key="chart2")

    with tab2:
        st.subheader("Detección de Anomalías")
        
        # Timeline of anomalies
        fig3 = px.scatter(
            df_view.reset_index(), 
            x='index', 
            y='consumption', 
            color='anomaly', 
            hover_data=['ocupacion', 'recommendation'],
            color_discrete_map={1: 'blue', -1: 'red'},
            title="Detección de Anomalías (Rojo = Anómalo)"
        )
        st.plotly_chart(fig3, key="chart3")
        
        st.markdown("### 💡 Recomendaciones Generadas")
        # Show recent recommendations
        rec_df = df_view[df_view['recommendation'] != "Operación normal"].tail(10)
        if not rec_df.empty:
            for index, row in rec_df.iterrows():
                with st.expander(f"{index} - {row['sector']}"):
                    st.write(f"**Detectado:** {row['recommendation']}")
                    st.write(f"**Consumo:** {row['consumption']:.2f} kWh | **Ocupación:** {row['ocupacion']}")
        else:
            st.info("No hay recomendaciones urgentes recientes.")

    with tab3:
        st.subheader("Asistente de Inteligencia Energética (XAI)")
        st.write("Pregunta sobre los datos, patrones o justificación de las recomendaciones.")
        
        # API Key handling (In production, use secrets)
        api_key = st.text_input("Groq API Key (opcional si ya está configurada)", type="password")
        
        # Use default if available (passed from env or script)
        # Note: In the user script, the key was hardcoded. We should probably accept it or use env var.
        # For now, let's look for env var or hardcoded fallback (not secure but per user request snippet)
        
        # user snippet key default fallback is kept for convenience but driven by env
        default_key = os.environ.get("GROQ_API_KEY", "")
        
        if not api_key:
            api_key = default_key
            
        if api_key:
            query = st.chat_input("Ej: ¿Por qué el consumo fue alto en Tunja ayer?")
            if query:
                with st.chat_message("user"):
                    st.write(query)
                
                with st.chat_message("assistant"):
                    try:
                        # Model updated to llama-3.3-70b-versatile as llama3-8b-8192 is decommissioned
                        llm = ChatGroq(temperature=0, groq_api_key=api_key, model_name="llama-3.3-70b-versatile")
                        # We use a subset of data for the agent to avoid token limits
                        # Let's give it the last 1000 rows or summarized data
                        agent_df = df_view.tail(1000)
                        st.write("Analizando datos...") # Feedback inicial
                        agent = create_pandas_dataframe_agent(
                            llm, 
                            agent_df, 
                            verbose=True, 
                            allow_dangerous_code=True
                        )
                        with st.spinner("Consultando a la IA..."):
                            res = agent.invoke({"input": query})
                            if isinstance(res, dict) and "output" in res:
                                st.write(res["output"])
                            else:
                                st.write(res)
                    except Exception as e:
                        st.error(f"Error del asistente: {e}")
        else:
            st.warning("Por favor ingresa una API Key de Groq para usar el asistente.")

if __name__ == "__main__":
    main()
