import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(BASE_DIR, "../results")
DATA_PATH = os.path.join(RESULTS_DIR, "anomalies_detected.csv")

def analyze_inefficiencies():
    print("Loading anomaly data...")
    try:
        df = pd.read_csv(DATA_PATH)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # 1. Phantom Consumption (High Usage vs Low Occupancy)
        # Definition: Top 25% of consumption while occupancy < 5%
        print("Detecting Phantom Consumption...")
        low_occ_threshold = 5 
        high_energy_threshold = df.groupby('sede')['energia_total_kwh'].transform(lambda x: x.quantile(0.75))
        
        df['phantom_waste'] = (df['ocupacion_pct'] < low_occ_threshold) & (df['energia_total_kwh'] > high_energy_threshold)
        
        phantom_kwh = df.loc[df['phantom_waste'], 'energia_total_kwh'].sum()
        print(f"Total Phantom Waste Detected: {phantom_kwh:,.2f} kWh")
        
        # 2. Nighttime Inefficiency (Academic areas active at night)
        # Definition: Salones/Auditorios > 0 kWh between 23:00 and 05:00
        print("Detecting Nighttime Waste...")
        night_hours = [23, 0, 1, 2, 3, 4]
        
        # We need sector columns. They are in the clean csv.
        # Check if high consumption in Salones/Auditorios at night
        # We assume baseline "standby" is low. If it exceeds breakdown, it's waste.
        # Let's say > 10% of daytime peak.
        
        # For simplicity in this hackathon scope: simple threshold > 0 is too strict (always some standby).
        # Let's use > 50 kWh as a heuristic for "Lights Left On".
        
        cols_academic = ['energia_salones_kwh', 'energia_auditorios_kwh']
        df['night_waste'] = (df['hour'].isin(night_hours)) & (df[cols_academic].sum(axis=1) > 50)
        
        night_kwh = df.loc[df['night_waste'], cols_academic].sum(axis=1).sum()
        print(f"Total Nighttime Waste Detected: {night_kwh:,.2f} kWh")
        
        # Save Report
        waste_summary = pd.DataFrame({
            'Category': ['Phantom Consumption (Low Occ, High Energy)', 'Nighttime Waste (Academic Areas)'],
            'Total_kWh_Wasted': [phantom_kwh, night_kwh],
            'Cost_Est_COP': [phantom_kwh * 800, night_kwh * 800] # Approx 800 COP/kWh
        })
        
        print("\n--- Inefficiency Summary ---")
        print(waste_summary)
        waste_summary.to_csv(os.path.join(RESULTS_DIR, "waste_summary.csv"), index=False)
        
        # Save detailed flags
        df.to_csv(os.path.join(RESULTS_DIR, "detailed_inefficiencies.csv"), index=False)
        
    except FileNotFoundError:
        print("anomalies_detected.csv not found.")

if __name__ == "__main__":
    analyze_inefficiencies()
