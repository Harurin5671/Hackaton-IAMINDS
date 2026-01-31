import pandas as pd
import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

# Setup
load_dotenv() # Load stored keys if available
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_PATH = os.path.join(BASE_DIR, "../results/prioritized_recommendations.csv")
OUTPUT_PATH = os.path.join(BASE_DIR, "../results/advisor_report.md")

# Default Grid Key if not in Env (using the one from user history for continuity)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def generate_recommendations():
    print("Initializing LLM Advisor...")
    try:
        df = pd.read_csv(INPUT_PATH)
        # Take top 3 for demo to save time/tokens
        top_events = df.head(3)
        
        llm = ChatGroq(temperature=0.3, groq_api_key=GROQ_API_KEY, model_name="llama-3.1-8b-instant")
        
        template = """
        ACT: You are a Senior Energy Efficiency Engineer at UPTC University.
        TASK: Analyze this energy anomaly and write a SHORT, ACTIONABLE recommendation card for the Facility Manager.
        
        CONTEXT:
        - Sede: {sede}
        - Category: {category}
        - Duration: {duration} hours
        - Total Waste: {kwh} kWh
        - Time: {start} to {end}
        - Avg Occupancy: {occ}%
        
        REQUIREMENTS:
        1. Title: Urgent Action Required - [Location]
        2. Diagnosis: 1 sentence explaining why this is abnormal.
        3. Action: 2 specific technical steps to fix it (e.g., check timers, HVAC sensors).
        4. Tone: Professional, urgent but helpful.
        5. Language: Spanish.
        
        OUTPUT: Markdown format.
        """
        
        prompt = PromptTemplate(
            template=template,
            input_variables=["sede", "category", "duration", "kwh", "start", "end", "occ"]
        )
        
        chain = prompt | llm
        
        report_content = "# 🛡️ Reporte Diario de Eficiencia Energética (IA)\n\n"
        
        print(f"Generating reports for {len(top_events)} critical events...")
        
        for idx, row in top_events.iterrows():
            print(f"  Processing Event {row['event_id']}...")
            response = chain.invoke({
                "sede": row['sede'],
                "category": row['category'],
                "duration": row['duration_hours'],
                "kwh": f"{row['total_kwh']:.2f}",
                "start": row['start_time'],
                "end": row['end_time'],
                "occ": f"{row['avg_occupancy']:.1f}"
            })
            
            report_content += f"## Evento #{idx+1} (ID: {row['event_id']})\n"
            report_content += response.content + "\n\n---\n\n"
            
        # Save
        with open(OUTPUT_PATH, "w") as f:
            f.write(report_content)
            
        print(f"Report saved to {OUTPUT_PATH}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    generate_recommendations()
