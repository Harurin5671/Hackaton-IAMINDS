import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PHASE2_RESULTS = os.path.join(BASE_DIR, "../../phase-2-anomalies/results")
RESULTS_DIR = os.path.join(BASE_DIR, "../results")
os.makedirs(RESULTS_DIR, exist_ok=True)

# Constants
CO2_FACTOR_KG_KWH = 0.164  # Colombia Grid Average
COST_COP_KWH = 800         # Avg Industrial/University Rate

def calculate_impact():
    print("Calculating Impact Metrics...")
    try:
        # Load Waste from Phase 2
        df_waste = pd.read_csv(os.path.join(PHASE2_RESULTS, "waste_summary.csv"))
        
        # Calculate totals
        total_waste_kwh = df_waste['Total_kWh_Wasted'].sum()
        
        # We assume we can save 100% of 'Waste' (ideal) or 80% (realistic).
        # Let's report "Potential Savings"
        
        savings_kwh = total_waste_kwh
        savings_co2 = savings_kwh * CO2_FACTOR_KG_KWH
        savings_cop = savings_kwh * COST_COP_KWH
        
        # Create Report
        impact_data = {
            'Metric': ['Energy Saved', 'CO2 Avoided', 'Economic Savings'],
            'Value': [savings_kwh, savings_co2, savings_cop],
            'Unit': ['kWh', 'kg CO2', 'COP']
        }
        
        df_impact = pd.DataFrame(impact_data)
        
        print("\n--- Impact Report ---")
        print(df_impact)
        
        df_impact.to_csv(os.path.join(RESULTS_DIR, "impact_report.csv"), index=False)
        print(f"Report saved to {RESULTS_DIR}")
        
    except FileNotFoundError:
        print("Waste summary not found. Run Phase 2 first.")

if __name__ == "__main__":
    calculate_impact()
