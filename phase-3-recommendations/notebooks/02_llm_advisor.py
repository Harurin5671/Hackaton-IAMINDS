import pandas as pd
import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

# Setup
load_dotenv()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_PATH = os.path.join(BASE_DIR, "../results/prioritized_recommendations.csv")
OUTPUT_MD_PATH = os.path.join(BASE_DIR, "../results/advisor_report.md")
# We will overwrite the input CSV to include the new AI column, or save to a new one. 
# Overwriting is easier for the API since it already reads this file.
OUTPUT_CSV_PATH = INPUT_PATH 

# Config
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
COST_PER_KWH = 800  # Pesos Colombianos

def generate_recommendations():
    print("Initializing Advanced LLM Advisor (Expert Mode)...")
    try:
        df = pd.read_csv(INPUT_PATH)
        
        # Ensure we have a column for the AI text
        if 'ai_recommendation' not in df.columns:
            df['ai_recommendation'] = "Pending..."
            
        # We process the top 5 events for the demo
        top_indices = df.head(5).index
        
        # 1. Try OpenAI (Paid & Stable)
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            try:
                from langchain_openai import ChatOpenAI
                llm = ChatOpenAI(temperature=0.3, model_name="gpt-4o-mini", openai_api_key=openai_key)
                print("Using OpenAI (gpt-4o-mini)")
            except:
                print("OpenAI key found but library missing. Installing fallback...")
                llm = None
        else:
            llm = None

        # 2. Fallback to Groq
        if not llm:
            api_key = os.getenv("GROQ_API_KEY")
            llm = ChatGroq(temperature=0.4, groq_api_key=api_key, model_name="llama-3.3-70b-versatile")
            print("Using Groq (llama-3.3-70b)")
        
        # PROMPT ENGINEERING V3: User-Friendly & Actionable
        template = """
        ACT AS: Energy Efficiency Expert.
        AUDIENCE: Facility Managers (Non-technical).
        
        INPUT DATA:
        - Location: {sede}
        - Anomaly: {category} (Duration: {duration}h)
        - Wasted Energy: {kwh} kWh
        - Cost: ${cost} COP
        - Time: {start} to {end}
        - Occupancy: {occ}%
        
        TASK: Write a SHORT, CLEAR advice card in Spanish.
        
        FORMAT (Strictly follow this structure):
        
        # 🚨 [Title: Short & Descriptive] (e.g. "Consumo Nocturno Inesperado")
        
        **Problema:**
        [One simple sentence explaining what happened. e.g. "Detectamos encendido de equipos a las 3 AM sin personal."]
        
        **Impacto:**
        Costó aprox **${cost} COP** desperdiciados.
        
        **Acción Inmediata:**
        *   [Action 1: Specific & Imperative. e.g. "Revisar termostato en Cafetería"]
        *   [Action 2: Simple step]
        
        TONE: Helpful, Urgent, Professional.
        LANGUAGE: Spanish (Colombia).
        LENGTH: Keep it short. No fluff.
        """
        
        prompt = PromptTemplate(
            template=template,
            input_variables=["sede", "category", "duration", "kwh", "cost", "start", "end", "occ"]
        )
        
        chain = prompt | llm
        
        report_content = "# 🛡️ Reporte Estratégico de Eficiencia (Executive Summary)\n\n"
        
        print(f"Generating strategic reports for {len(top_indices)} events...")
        
        for idx in top_indices:
            row = df.loc[idx]
            print(f"  Analysing Event {row['event_id']}...")
            
            # Calculate cost
            cost = row['total_kwh'] * COST_PER_KWH
            
            response = chain.invoke({
                "sede": row['sede'],
                "category": row['category'],
                "duration": row['duration_hours'],
                "kwh": f"{row['total_kwh']:.0f}",
                "cost": f"{cost:,.0f}",
                "start": row['start_time'],
                "end": row['end_time'],
                "occ": f"{row['avg_occupancy']:.1f}"
            })
            
            # Save to DataFrame column
            df.at[idx, 'ai_recommendation'] = response.content
            
            # Append to MD report
            report_content += f"## Evento {row['event_id']}\n"
            report_content += response.content + "\n\n---\n\n"
            
        # Save CSV (so API can serve it)
        df.to_csv(OUTPUT_CSV_PATH, index=False)
        print(f"Updated CSV with AI recommendations at {OUTPUT_CSV_PATH}")

        # Save MD (for documentation)
        with open(OUTPUT_MD_PATH, "w") as f:
            f.write(report_content)
        print(f"Strategic Report saved to {OUTPUT_MD_PATH}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    generate_recommendations()
