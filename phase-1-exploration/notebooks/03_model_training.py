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
    df_consumos = pd.read_csv(os.path.join(DATA_DIR, "consumos_uptc_clean.csv"))
    df_sedes = pd.read_csv(os.path.join(DATA_DIR, "sedes_uptc.csv"))
    df = pd.merge(df_consumos, df_sedes, on='sede_id', how='left', suffixes=('', '_info_sede'))

    bool_cols = ['tiene_residencias', 'tiene_laboratorios_pesados']
    for col in bool_cols:
        if col in df.columns:
            df[col] = df[col].fillna(0).astype(int)

    print(f"Merge completado. Nuevas columnas añadidas: {df_sedes.columns.tolist()}")


    df['timestamp'] = pd.to_datetime(df['timestamp'])
    # Feature Engineering (Encoding Categoricals)
    df['sede_id_encoded'] = df['sede'].astype('category').cat.codes
    # Feature Engineering (Encoding Categoricals)
    df['sede_id_encoded'] = df['sede'].astype('category').cat.codes
    df['periodo_academico_encoded'] = df['periodo_academico'].astype('category').cat.codes
    
    # Define Target
    TARGET = 'energia_total_kwh'
    
    # --- 1. MEJORA DE DATOS (Interpolación y Lags) ---
    print("Generating Advanced Features (Lags & Interpolation)...")
    df = df.sort_values(['sede', 'timestamp'])
    
    # Dia Laboral (Lun-Vie)
    df['es_dia_laboral'] = df['timestamp'].dt.dayofweek.isin([0,1,2,3,4]).astype(int)
    
    # Rellenar huecos en temperatura y ocupación
    df['temperatura_exterior_c'] = df.groupby('sede')['temperatura_exterior_c'].transform(lambda x: x.interpolate().ffill().bfill())
    df['ocupacion_pct'] = df.groupby('sede')['ocupacion_pct'].transform(lambda x: x.interpolate().ffill().bfill())

    # Generar Lags incluyendo el de 1 HORA
    df['lag_1h'] = df.groupby('sede')[TARGET].shift(1) 
    df['lag_24h'] = df.groupby('sede')[TARGET].shift(24)
    df['lag_168h'] = df.groupby('sede')[TARGET].shift(168)
    
    # Borrar filas sin historia
    df = df.dropna(subset=['lag_1h', 'lag_24h', 'lag_168h']).reset_index(drop=True)

    # --- 2. LISTA DE FEATURES FORTALECIDA ---
    FEATURES = [
        'hour_sin', 'hour_cos', 'day_sin', 'day_cos', 'month_sin', 'month_cos',
        'temperatura_exterior_c', 'ocupacion_pct',
        'es_festivo', 'es_semana_parciales', 'es_semana_finales', 'es_dia_laboral',
        'sede_id_encoded', 'periodo_academico_encoded',
        'lag_1h', 'lag_24h', 'lag_168h', # Lags completos
        'area_m2', 'num_estudiantes', 'altitud_msnm', 'tiene_laboratorios_pesados'
    ]
    
    # Train/Test Split (Time-based)
    split_date = '2025-01-01'
    train = df[df['timestamp'] < split_date].copy()
    test = df[df['timestamp'] >= split_date].copy()
    
    # --- OUTLIER REMOVAL (Clean Training Data) ---
    print("Removing Outliers from Training Data (1% top/bottom per Sede)...")
    train_clean_list = []
    for sede in train['sede'].unique():
        s_df = train[train['sede'] == sede]
        q_low = s_df[TARGET].quantile(0.01)
        q_high = s_df[TARGET].quantile(0.99)
        s_clean = s_df[(s_df[TARGET] >= q_low) & (s_df[TARGET] <= q_high)]
        train_clean_list.append(s_clean)
    train = pd.concat(train_clean_list)
    print(f"Cleaned Train size: {train.shape}, Test size: {test.shape}")
    
    # --- 3. ENTRENAMIENTO GLOBAL (No por sede) ---
    print("\nTraining GLOBAL XGBoost Model (All Sedes together)...")
    
    model = xgb.XGBRegressor(
        n_estimators=1500,
        learning_rate=0.01,
        max_depth=8,        # Increased to 8 as requested
        subsample=0.8,
        colsample_bytree=0.8,
        reg_alpha=0.1,
        early_stopping_rounds=50,
        n_jobs=-1
    )

    # Fit Global
    model.fit(
        train[FEATURES], train[TARGET],
        eval_set=[(train[FEATURES], train[TARGET]), (test[FEATURES], test[TARGET])],
        verbose=100
    )
    
    # Predict on ALL test data (Validation)
    test['prediction'] = model.predict(test[FEATURES])
    
    # --- METRICS PER SEDE ---
    metrics = []
    print("\n--- Validation Metrics by Sede ---")
    
    sedes = df['sede'].unique()
    for sede in sedes:
        test_s = test[test['sede'] == sede]
        
        # Evaluate
        rmse = np.sqrt(mean_squared_error(test_s[TARGET], test_s['prediction']))
        mae = mean_absolute_error(test_s[TARGET], test_s['prediction'])
        
        # Calculate R2
        from sklearn.metrics import r2_score
        r2 = r2_score(test_s[TARGET], test_s['prediction'])
        
        # Calculate MAPE
        y_true = test_s[TARGET]
        mask = y_true > 0
        if mask.any():
            mape = np.mean(np.abs((y_true[mask] - test_s['prediction'][mask]) / y_true[mask])) * 100
        else:
            mape = 0
        
        accuracy_pct = 100 - mape
        
        print(f"Sede: {sede}")
        print(f"  RMSE: {rmse:.2f} | MAE: {mae:.2f}")
        print(f"  R2 Score: {r2:.2f}")
        print(f"  MAPE: {mape:.2f}% | Accuracy: {accuracy_pct:.2f}%")
        
        metrics.append({
            'sede': sede, 'rmse': rmse, 'mae': mae, 'r2': r2, 'accuracy_pct': accuracy_pct
        })

    # Save metrics
    metrics_df = pd.DataFrame(metrics)
    print("\n--- Final Global Metrics Summary ---")
    print(metrics_df)
    metrics_df.to_csv(os.path.join(PLOTS_DIR, "metrics.csv"), index=False)
    
    # Plot Prediction vs Actual (First month 2025)
    plot_df = test[(test['timestamp'] >= '2025-01-01') & (test['timestamp'] < '2025-02-01')]
    
    plot_melt = plot_df.melt(id_vars=['timestamp', 'sede'], value_vars=[TARGET, 'prediction'], 
                            var_name='Tipo Dato', value_name='kWh')
    plot_melt['Tipo Dato'] = plot_melt['Tipo Dato'].replace({TARGET: 'Real (Historia)', 'prediction': 'Predicción IA'})
    
    fig = px.line(plot_melt, x='timestamp', y='kWh', color='Tipo Dato', line_dash='sede',
                  title='Validación Global Final: Real vs Predicho (Enero 2025)',
                  color_discrete_map={'Real (Historia)': '#00FFFF', 'Predicción IA': '#FFA500'},
                  template='plotly_dark')
    
    validation_path = os.path.join(PLOTS_DIR, "accuracy_validation_2025.html")
    fig.write_html(validation_path)
    print(f"Validation Plot saved to: {validation_path}")

    # --- FORECASTING FUTURE (Full Year 2026) ---
    print("\n--- Generating Future Forecast (Full Year 2026) using Global Model ---")
    
    future_preds = []
    
    # Pre-calculate 2025 history for Lag Mapping
    history_2025_full = df[df['timestamp'].dt.year == 2025].copy()
    
    # Generate future dataframe per sede (features need to be specific per sede)
    for sede in sedes:
        sede_df = df[df['sede'] == sede] # Reference for static values
        
        # Future dates: 2026
        future_dates = pd.date_range(start='2026-01-01', end='2026-12-31 23:00:00', freq='h')
        future_df = pd.DataFrame({'timestamp': future_dates})
        future_df['sede'] = sede
        
        # Cyclical Features
        future_df['hour_sin'] = np.sin(2 * np.pi * future_df['timestamp'].dt.hour / 24)
        future_df['hour_cos'] = np.cos(2 * np.pi * future_df['timestamp'].dt.hour / 24)
        future_df['day_sin'] = np.sin(2 * np.pi * future_df['timestamp'].dt.dayofweek / 7)
        future_df['day_cos'] = np.cos(2 * np.pi * future_df['timestamp'].dt.dayofweek / 7)
        future_df['month_sin'] = np.sin(2 * np.pi * future_df['timestamp'].dt.month / 12)
        future_df['month_cos'] = np.cos(2 * np.pi * future_df['timestamp'].dt.month / 12)
        
        # Missing Feature for Global Model
        future_df['es_dia_laboral'] = future_df['timestamp'].dt.dayofweek.isin([0,1,2,3,4]).astype(int)
        
        # Feature Mapping (2025 -> 2026)
        source_2025 = history_2025_full[history_2025_full['sede'] == sede].copy()
        source_2025['join_key'] = source_2025['timestamp'].apply(lambda x: f"{x.month}-{x.day}-{x.hour}")
        future_df['join_key'] = future_df['timestamp'].apply(lambda x: f"{x.month}-{x.day}-{x.hour}")
        
        cols_to_map = ['temperatura_exterior_c', 'ocupacion_pct', 'energia_total_kwh'] 
        future_df = future_df.merge(source_2025[['join_key'] + cols_to_map], on='join_key', how='left')
        future_df[cols_to_map] = future_df[cols_to_map].ffill().bfill()
        
        # Static Features (Copy from sede_df)
        static_cols = ['area_m2', 'num_estudiantes', 'altitud_msnm', 'tiene_laboratorios_pesados']
        for col in static_cols:
            if col in sede_df.columns:
                future_df[col] = sede_df[col].iloc[0]
            else:
                future_df[col] = 0
                
        # Lags Assignment
        # Using 2025 data as proxy for 2026 lags
        future_df['lag_1h'] = future_df['energia_total_kwh'] # Simplified proxy
        future_df['lag_24h'] = future_df['energia_total_kwh']
        future_df['lag_168h'] = future_df['energia_total_kwh']
        
        # Categoricals defaults
        future_df['es_festivo'] = 0 
        future_df['es_semana_parciales'] = 0
        future_df['es_semana_finales'] = 0
        if 'sede_id_encoded' in sede_df.columns:
            future_df['sede_id_encoded'] = sede_df['sede_id_encoded'].iloc[0]
        if 'periodo_academico_encoded' in sede_df.columns:
            future_df['periodo_academico_encoded'] = sede_df['periodo_academico_encoded'].mode()[0]
            
        # Predict using mapped features and GLOBAL model
        future_df['pred_energy_kwh'] = model.predict(future_df[FEATURES])
        future_df['type'] = 'Pronostico 2026'
        
        # Cleanup
        future_df = future_df.drop(columns=['join_key', 'energia_total_kwh'])
        future_preds.append(future_df)
        
    final_forecast = pd.concat(future_preds)
    csv_path = os.path.join(PLOTS_DIR, "forecast_2026_full.csv")
    final_forecast.to_csv(csv_path, index=False)
    print(f"Forecast saved to {csv_path}")
        
    final_forecast = pd.concat(future_preds)
    csv_path = os.path.join(PLOTS_DIR, "forecast_2026_full.csv")
    final_forecast.to_csv(csv_path, index=False)
    print(f"Forecast saved to {csv_path}")
    
    # --- PLOT GENERATION ---
    # Visualize 2025 (History) vs 2026 (Forecast) for validation
    history_2025 = df[df['timestamp'].dt.year == 2025].copy()
    history_2025['type'] = 'Historia 2025'
    history_2025 = history_2025.rename(columns={TARGET: 'energy'})
    
    forecast_viz = final_forecast.rename(columns={'pred_energy_kwh': 'energy'})
    
    combined = pd.concat([
        history_2025[['timestamp', 'energy', 'sede', 'type']],
        forecast_viz[['timestamp', 'energy', 'sede', 'type']]
    ])
    
    # Daily aggregation for cleaner plot
    daily = combined.groupby(['sede', 'type', pd.Grouper(key='timestamp', freq='D')])['energy'].sum().reset_index()
    
    fig_html = px.line(daily, x='timestamp', y='energy', color='sede', line_dash='type',
                       title='Validación: Historia 2025 vs Pronóstico 2026', template='plotly_dark')
    
    html_path = os.path.join(PLOTS_DIR, "forecast_2026_plot.html")
    fig_html.write_html(html_path)
    print(f"HTML Plot saved to {html_path}")

if __name__ == "__main__":
    train_model()
