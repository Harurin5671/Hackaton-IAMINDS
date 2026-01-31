import streamlit as st
import pandas as pd
import plotly.express as px
import os
import sys
import traceback

from dotenv import load_dotenv
try:
    from langchain_groq import ChatGroq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

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

def offline_assistant_answer(user_question: str, sede: str, anom_df, recs_df) -> str:
    """
    Fallback offline: responde con datos ya calculados (anomalías + recomendaciones).
    No usa LLM.
    """
    q = (user_question or "").lower().strip()

    # 1) Recomendaciones priorizadas para la sede
    sede_recs = recs_df[recs_df["sede"] == sede].copy() if not recs_df.empty else recs_df
    sede_recs = sede_recs.sort_values("total_kwh", ascending=False).head(3) if not sede_recs.empty else sede_recs

    # 2) Últimas anomalías críticas para la sede
    sede_anom = anom_df[anom_df["sede"] == sede].copy() if "sede" in anom_df.columns else anom_df.copy()
    if "anomaly_critical" in sede_anom.columns:
        sede_anom = sede_anom[sede_anom["anomaly_critical"] == 1].copy()
    if "timestamp" in sede_anom.columns:
        sede_anom["timestamp"] = pd.to_datetime(sede_anom["timestamp"], errors="coerce")
        sede_anom = sede_anom.sort_values("timestamp", ascending=False).head(5)

    # Respuestas “tipo” según intención simple
    if any(k in q for k in ["recomend", "acción", "hacer", "suger", "reducir"]):
        if sede_recs.empty:
            return "No tengo recomendaciones priorizadas disponibles para esta sede en este momento."
        lines = ["**Modo offline — Recomendaciones priorizadas (Top 3):**"]
        for _, r in sede_recs.iterrows():
            lines.append(
                f"- **{r['category']}** ({r['start_time']} → {r['end_time']}): "
                f"~{r['total_kwh']:.1f} kWh en {int(r['duration_hours'])}h, ocupación prom. {r['avg_occupancy']:.1f}%."
            )
        lines.append("\nTip: revisa el tab **🚨 Alertas & Recomendaciones** para el detalle de cada evento.")
        return "\n".join(lines)

    if any(k in q for k in ["anomal", "alert", "pico", "desperd", "waste", "crític"]):
        if sede_anom.empty:
            return "No tengo anomalías críticas recientes registradas para esta sede."
        lines = ["**Modo offline — Últimas anomalías críticas (Top 5):**"]
        for _, a in sede_anom.iterrows():
            ts = a["timestamp"]
            kwh = a.get("energia_total_kwh", float("nan"))
            occ = a.get("ocupacion_pct", float("nan"))
            lines.append(f"- {ts}: energía={kwh if pd.notna(kwh) else 'NA'} kWh, ocupación={occ if pd.notna(occ) else 'NA'}%")
        lines.append("\nTip: revisa el tab **📊 Analítica** para ver el patrón base.")
        return "\n".join(lines)

    # Default: mezcla
    parts = []
    if not sede_recs.empty:
        parts.append("**Modo offline — Resumen rápido**")
        r = sede_recs.iloc[0]
        parts.append(f"- Recomendación #1: **{r['category']}** (~{r['total_kwh']:.1f} kWh)")
    if not sede_anom.empty:
        a = sede_anom.iloc[0]
        parts.append(f"- Última anomalía crítica: {a['timestamp']} (energía {a['energia_total_kwh']:.1f} kWh)")
    if not parts:
        parts = ["Modo offline activo, pero no hay datos suficientes cargados para responder."]
    parts.append("\nPuedes preguntar: *'¿Qué acciones puedo tomar?'* o *'¿Qué anomalías hay?'*")
    return "\n".join(parts)

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
        st.plotly_chart(fig, use_container_width=True)
          
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
        
        user_question = st.chat_input("Haz una pregunta sobre consumo, anomalías o acciones...")

        if user_question:
            st.chat_message("user").write(user_question)

            # Si no hay key o no hay librería, vamos offline
            has_key = bool(os.getenv("GROQ_API_KEY"))
            if (not GROQ_AVAILABLE) or (not has_key):
                st.warning("Asistente IA no disponible (GROQ). Activando modo offline.")
                ans = offline_assistant_answer(user_question, sede_sel, anom_view, df_recs)
                st.chat_message("assistant").write(ans)
            else:
                try:
                    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.2)

                    # (aquí el agente, lo optimizamos en la Solución 2)
                    agent = create_pandas_dataframe_agent(
                        llm,
                        anom_view.tail(200),  # ya reducimos un poco
                        verbose=False,
                        allow_dangerous_code=False
                    ) 

                    response = agent.invoke(user_question)
                    output = response.get("output") if isinstance(response, dict) else str(response)
                    st.chat_message("assistant").write(output)

                except Exception as e:
                    st.warning("Groq falló o se agotó la cuota. Activando modo offline.")
                    # opcional: imprimir error en consola
                    print("LLM error:", repr(e))
                    # print(traceback.format_exc())

                    ans = offline_assistant_answer(user_question, sede_sel, anom_view, df_recs)
                    st.chat_message("assistant").write(ans)


if __name__ == "__main__":
    main()
