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
        
        # Using Llama-3-70b for maximum reasoning capability
        llm = ChatGroq(temperature=0.4, groq_api_key=GROQ_API_KEY, model_name="llama-3.3-70b-versatile")
        
        # PROMPT ENGINEERING V2: Role-Playing + Business Impact
        template = """
        ROLE: You are a Senior Energy Strategy Consultant hired by the University Board.
        YOUR GOAL: Explain energy waste to the Board of Directors (who are NOT engineers). They care about Money, Reputation, and Sustainability.
        
        INPUT DATA:
        - Location: {sede}
        - Problem Type: {category} (Duration: {duration} hours)
        - Energy Wasted: {kwh} kWh
        - Estimated Cost: ${cost} COP
        - Context: Time {start} to {end} | Occupancy was {occ}% (very low)
        
        DOMAIN KNOWLEDGE CHEAT SHEET:
        - Kitchens: Often leave industrial freezers open or ovens on cleaning cycles.
        - Classrooms: Lights left on, Projectors in standby, Windows open while AC is on.
        - Labs: Compressors, Centrifuges, or fume hoods left running.
        - Offices: Computers not sleeping, personal heaters.
        
        TASK: Write a "Critical Incident Card" in Markdown.
        
        STRUCTURE REQUIRED:
        ### 🚨 [Catchy Headline in Spanish]
        
        **📉 What happened?**
        (1 simple sentence in Spanish. Explain clearly. E.g., "While nobody was on campus, the machinery kept running at full power.")
        
        **💸 The Cost**
        "This incident alone cost the university approx **${cost} COP**."
        
        **🛠️ Immediate Fix (The "Quick Win")**
        1. [Actionable step 1]
        2. [Actionable step 2]
        
        **🔮 Long-term Strategy**
        (1 sentence recommendation like "Install motion sensors" or "Change Shift policy")
        
        TONE: Professional, Direct, Urgent.
        LANGUAGE: Spanish (Colombia).
        NO PREAMBLE. JUST THE MARKDOWN CARD.
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
