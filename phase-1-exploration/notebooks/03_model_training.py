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
    
    # Feature Engineering (Encoding Categoricals)
    df['sede_id_encoded'] = df['sede'].astype('category').cat.codes
    df['periodo_academico_encoded'] = df['periodo_academico'].astype('category').cat.codes

    # Target and Features
    TARGET = 'energia_total_kwh'
    FEATURES = ['hour_sin', 'hour_cos', 'day_sin', 'day_cos', 'month_sin', 'month_cos', 
                'temperatura_exterior_c', 'ocupacion_pct',
                'es_festivo', 'es_semana_parciales', 'es_semana_finales',
                'sede_id_encoded', 'periodo_academico_encoded']
    
    # Sorting
    df = df.sort_values(['sede', 'timestamp'])
    
    # Train/Test Split (Time-based)
    # Train: < 2025, Test: >= 2025
    split_date = '2025-01-01'
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
            n_estimators=700,
            learning_rate=0.02,
            max_depth=5,
            early_stopping_rounds=100,
            n_jobs=-3
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
        
        # Calculate R2
        from sklearn.metrics import r2_score
        r2 = r2_score(test_s[TARGET], preds)
        
        # Calculate MAPE (Mean Absolute Percentage Error)
        # Handle division by zero if target is 0
        y_true = test_s[TARGET]
        mask = y_true > 0
        if mask.any():
            mape = np.mean(np.abs((y_true[mask] - preds[mask]) / y_true[mask])) * 100
        else:
            mape = 0
            
        accuracy_pct = 100 - mape
        
        print(f"  RMSE: {rmse:.2f} | MAE: {mae:.2f}")
        print(f"  R2 Score: {r2:.2f}")
        print(f"  MAPE: {mape:.2f}%")
        print(f"  >> PRECISION (Accuracy): {accuracy_pct:.2f}%")
        
        metrics.append({
            'sede': sede, 
            'rmse': rmse, 
            'mae': mae, 
            'r2': r2, 
            'accuracy_pct': accuracy_pct
        })
        
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
        plot_df = all_res[(all_res['timestamp'] >= '2025-01-01') & (all_res['timestamp'] < '2025-01-15')]
        
        fig = px.line(plot_df, x='timestamp', y=[TARGET, 'prediction'], color='sede',
                      title='Actual vs Predicted Energy (Jan 2025)')
        fig.write_html(os.path.join(PLOTS_DIR, "prediction_comparison.html"))
        print("Saved prediction_comparison.html")

if __name__ == "__main__":
    train_model()
