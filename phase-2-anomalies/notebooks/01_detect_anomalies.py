import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
import xgboost as xgb
import plotly.express as px
import os
import sys

# Setup Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "../../phase-1-exploration/data")
PHASE1_NOTEBOOKS = os.path.join(BASE_DIR, "../../phase-1-exploration/notebooks")
RESULTS_DIR = os.path.join(BASE_DIR, "../results")
os.makedirs(RESULTS_DIR, exist_ok=True)

# Add Phase 1 to path to import training logic if needed, 
# but for robustnes we'll implement a lightweight predictor here or load the CSV if we saved preds.
# Phase 1 script didn't save the FULL predictions to CSV, just the metrics and plots for a subset.
# So we will retrain a quick model here to get residuals for the whole dataset.

def get_residuals(df):
    print("Training reference model for Residual Analysis...")
    target = 'energia_total_kwh'
    features = ['hour_sin', 'hour_cos', 'day_sin', 'day_cos', 'month_sin', 'month_cos', 
                'temperatura_exterior_c', 'ocupacion_pct']
    
    # Simple model to get expected baseline
    model = xgb.XGBRegressor(n_estimators=100, max_depth=5, n_jobs=-1)
    
    # Train on all data (Unsupervised context: we want deviations from the "pattern", even if pattern learns some noise)
    # Ideally we train on "clean" data, but we use all here to find deviations from the *learned trend*.
    model.fit(df[features], df[target])
    
    df['predicted_consumption'] = model.predict(df[features])
    df['residual'] = df[target] - df['predicted_consumption']
    
    # Anomaly: Residual > 2 Std Dev (Unexplained High Consumption)
    std_resid = df['residual'].std()
    df['anomaly_residual'] = df['residual'] > (2 * std_resid)
    
    return df

def get_isolation_forest(df):
    print("Running Isolation Forest...")
    # Features for anomaly detection
    features = ['energia_total_kwh', 'ocupacion_pct', 'hour', 'dayofweek']
    
    # 2% contamination assumption
    iso = IsolationForest(contamination=0.02, random_state=42)
    
    # We fit per Sede to handle different scales
    df['anomaly_iso'] = 0
    
    for sede in df['sede'].unique():
        idx = df['sede'] == sede
        subset = df.loc[idx, features].fillna(0)
        
        # -1 is anomaly, 1 is normal. We convert -1 to True (1)
        preds = iso.fit_predict(subset)
        df.loc[idx, 'anomaly_iso'] = (preds == -1).astype(int)
        
    return df

def main():
    try:
        print("Loading data...")
        df = pd.read_csv(os.path.join(DATA_DIR, "consumos_uptc_clean.csv"))
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # 1. Residual Analysis
        df = get_residuals(df)
        
        # 2. Isolation Forest
        df = get_isolation_forest(df)
        
        # 3. Combine: Strong Anomaly if BOTH trigger
        df['anomaly_critical'] = ((df['anomaly_residual'] == True) & (df['anomaly_iso'] == 1)).astype(int)
        
        # Save
        output_path = os.path.join(RESULTS_DIR, "anomalies_detected.csv")
        df.to_csv(output_path, index=False)
        print(f"Anomalies saved to {output_path}")
        
        # Summary
        print("\n--- Anomaly Summary ---")
        print(df[['anomaly_residual', 'anomaly_iso', 'anomaly_critical']].sum())
        
        # Plot
        print("Plots...")
        # Visualizing the most critical anomalies
        anoms = df[df['anomaly_critical'] == 1]
        
        if not anoms.empty:
            fig = px.scatter(anoms.reset_index(), x='timestamp', y='energia_total_kwh', color='sede',
                             title='Critical Energy Anomalies Detected')
            fig.write_html(os.path.join(RESULTS_DIR, "critical_anomalies_scatter.html"))
        
    except FileNotFoundError:
        print("Clean data not found. Run Phase 1 preprocessing first.")

if __name__ == "__main__":
    main()
