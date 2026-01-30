import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.metrics import mean_squared_error, mean_absolute_error
import plotly.express as px
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "../data")
PLOTS_DIR = os.path.join(BASE_DIR, "../docs/model_plots")
os.makedirs(PLOTS_DIR, exist_ok=True)

def train_model():
    print("Loading clean data...")
    df = pd.read_csv(os.path.join(DATA_DIR, "consumos_uptc_clean.csv"))
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Target and Features
    TARGET = 'energia_total_kwh'
    FEATURES = ['hour_sin', 'hour_cos', 'day_sin', 'day_cos', 'month_sin', 'month_cos', 
                'temperatura_exterior_c', 'ocupacion_pct']
    # If we had lags, we'd add 'lag_24h' here. Let's compute it on the fly for simplicity.
    
    # Sorting
    df = df.sort_values(['sede', 'timestamp'])
    
    # Train/Test Split (Time-based)
    # Train: < 2024, Test: >= 2024
    split_date = '2024-01-01'
    train = df[df['timestamp'] < split_date].copy()
    test = df[df['timestamp'] >= split_date].copy()
    
    print(f"Train size: {train.shape}, Test size: {test.shape}")
    
    # Initialize metric storage
    metrics = []
    
    # Train separate models per Sede or Global? 
    # Global model with Sede as feature might capture general patterns better, but Sedes are distinct.
    # Let's try One Model per Sede for better accuracy.
    
    processed_dfs = []
    
    sedes = df['sede'].unique()
    for sede in sedes:
        print(f"\nTraining for Sede: {sede}")
        train_s = train[train['sede'] == sede]
        test_s = test[test['sede'] == sede]
        
        if train_s.empty or test_s.empty:
            print("  Skipping (insufficient data)")
            continue
            
        model = xgb.XGBRegressor(
            n_estimators=500,
            learning_rate=0.05,
            max_depth=6,
            early_stopping_rounds=50,
            n_jobs=-1
        )
        
        # Fit
        model.fit(
            train_s[FEATURES], train_s[TARGET],
            eval_set=[(train_s[FEATURES], train_s[TARGET]), (test_s[FEATURES], test_s[TARGET])],
            verbose=False
        )
        
        # Predict
        preds = model.predict(test_s[FEATURES])
        test_s['prediction'] = preds
        
        # Evaluate
        rmse = np.sqrt(mean_squared_error(test_s[TARGET], preds))
        mae = mean_absolute_error(test_s[TARGET], preds)
        
        print(f"  RMSE: {rmse:.2f} | MAE: {mae:.2f}")
        metrics.append({'sede': sede, 'rmse': rmse, 'mae': mae})
        
        processed_dfs.append(test_s)
        
    # Combine results for visualization
    all_res = pd.concat(processed_dfs) if processed_dfs else None
    
    if all_res is not None:
        # Save metrics
        metrics_df = pd.DataFrame(metrics)
        print("\n--- Final Metrics ---")
        print(metrics_df)
        metrics_df.to_csv(os.path.join(PLOTS_DIR, "metrics.csv"), index=False)
        
        # Plot Prediction vs Actual (First week of Test set for clarity)
        plot_df = all_res[(all_res['timestamp'] >= '2024-01-01') & (all_res['timestamp'] < '2024-01-15')]
        
        fig = px.line(plot_df, x='timestamp', y=[TARGET, 'prediction'], color='sede',
                      title='Actual vs Predicted Energy (Jan 2024)')
        fig.write_html(os.path.join(PLOTS_DIR, "prediction_comparison.html"))
        print("Saved prediction_comparison.html")

if __name__ == "__main__":
    train_model()
