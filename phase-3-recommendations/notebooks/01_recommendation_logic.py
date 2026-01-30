import pandas as pd
import numpy as np
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PHASE2_RESULTS = os.path.join(BASE_DIR, "../../phase-2-anomalies/results")
OUTPUT_DIR = os.path.join(BASE_DIR, "../results")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def categorize_anomaly(row):
    """
    Classifies the anomaly based on data context.
    """
    hour = row['hour']
    occ = row['ocupacion_pct']
    # Thresholds (calibrated from Phase 2 insights)
    
    # 1. Phantom (Low Occ, Anomaly)
    if occ < 5:
        return "Consumo Fantasma"
    
    # 2. Nighttime (Late hours)
    if hour > 22 or hour < 5:
        return "Uso Nocturno Inusual"
    
    # 3. High Load (Daytime peak but anomalous)
    return "Pico de Demanda Inesperado"

def aggregate_events(df):
    """
    Groups consecutive hourly anomalies into single 'Events' to avoid spamming.
    """
    print("Aggregating anomalies into events...")
    
    # Filter only anomalies
    anoms = df[df['anomaly_critical'] == 1].copy()
    
    # Apply category
    anoms['category'] = anoms.apply(categorize_anomaly, axis=1)
    
    # Sort
    anoms = anoms.sort_values(['sede', 'timestamp'])
    
    # Simple grouping: If same Sede, Same Category, and Time diff <= 3 hours, group them.
    anoms['time_diff'] = anoms.groupby('sede')['timestamp'].diff().dt.total_seconds() / 3600
    
    # New event if time diff > 3h or NaT (first)
    anoms['new_event'] = (anoms['time_diff'] > 3) | (anoms['time_diff'].isna())
    anoms['event_id'] = anoms.groupby('sede')['new_event'].cumsum()
    anoms['unique_event_id'] = anoms['sede'] + "_" + anoms['event_id'].astype(str)
    
    # Aggregate
    events = anoms.groupby('unique_event_id').agg({
        'sede': 'first',
        'timestamp': ['min', 'max'],
        'energia_total_kwh': 'sum',
        'ocupacion_pct': 'mean',
        'category': 'first',
        'reading_id': 'count' # Duration in hours
    }).reset_index()
    
    # Flatten columns
    events.columns = ['event_id', 'sede', 'start_time', 'end_time', 'total_kwh', 'avg_occupancy', 'category', 'duration_hours']
    
    # Rank by Impact (Total kWh)
    events = events.sort_values('total_kwh', ascending=False)
    
    return events

def main():
    try:
        input_path = os.path.join(PHASE2_RESULTS, "anomalies_detected.csv")
        df = pd.read_csv(input_path)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        events = aggregate_events(df)
        
        print("\n--- Top 5 Critical Events Identified ---")
        print(events.head())
        
        output_path = os.path.join(OUTPUT_DIR, "prioritized_recommendations.csv")
        events.to_csv(output_path, index=False)
        print(f"Events saved to {output_path}")
        
    except FileNotFoundError:
        print("Phase 2 anomalies not found.")

if __name__ == "__main__":
    main()
