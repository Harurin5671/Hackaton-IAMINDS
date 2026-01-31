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


SECTOR_COLS = [
    'energia_comedor_kwh',
    'energia_salones_kwh', 
    'energia_laboratorios_kwh',
    'energia_auditorios_kwh',
    'energia_oficinas_kwh'
]

def train_model_multisector():
    
    input_file = os.path.join(DATA_DIR, "consumos_uptc_clean.csv")
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"No se encontró el archivo {input_file}. Ejecuta 02_preprocessing.py primero.")
        
    df_consumos = pd.read_csv(input_file)
    df_sedes = pd.read_csv(os.path.join(DATA_DIR, "sedes_uptc.csv"))
    
    df = pd.merge(df_consumos, df_sedes, on='sede_id', how='left', suffixes=('', '_info_sede'))
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    bool_cols_to_fix = ['tiene_laboratorios_pesados', 'es_festivo', 'es_semana_parciales', 'es_semana_finales', 'tiene_residencias']
    for col in bool_cols_to_fix:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

    
    base_cols = ['timestamp', 'sede', 'sede_id', 'temperatura_exterior_c', 'ocupacion_pct', 
                 'dia_semana', 'es_festivo', 'es_semana_parciales', 'es_semana_finales',
                 'area_m2', 'num_estudiantes', 'altitud_msnm', 'tiene_laboratorios_pesados']
    
    base_cols = [c for c in base_cols if c in df.columns]
    
    df_long = df.melt(
        id_vars=base_cols,
        value_vars=SECTOR_COLS,
        var_name='sector_nombre',
        value_name='consumo_kwh'
    )
    
    df_long['sector_nombre'] = df_long['sector_nombre'].str.replace('energia_', '').str.replace('_kwh', '')
    
    print(f"   Datos transformados. Filas: {len(df_long)}. Sectores únicos: {df_long['sector_nombre'].unique()}")

    print("3. Generando Features...")
    df_long = df_long.sort_values(['sede', 'sector_nombre', 'timestamp'])
    
    df_long['es_dia_laboral'] = df_long['timestamp'].dt.dayofweek.isin([0,1,2,3,4]).astype(int)

    df_long['hour_sin'] = np.sin(2 * np.pi * df_long['timestamp'].dt.hour / 24)
    df_long['hour_cos'] = np.cos(2 * np.pi * df_long['timestamp'].dt.hour / 24)
    df_long['day_sin'] = np.sin(2 * np.pi * df_long['timestamp'].dt.dayofweek / 7)
    df_long['day_cos'] = np.cos(2 * np.pi * df_long['timestamp'].dt.dayofweek / 7)
    df_long['month_sin'] = np.sin(2 * np.pi * df_long['timestamp'].dt.month / 12)
    df_long['month_cos'] = np.cos(2 * np.pi * df_long['timestamp'].dt.month / 12)
    
    df_long['sector_encoded'] = df_long['sector_nombre'].astype('category').cat.codes
    df_long['sede_encoded'] = df_long['sede'].astype('category').cat.codes
    
    if 'periodo_academico' in df_long.columns: 
        df_long['periodo_academico_encoded'] = df_long['periodo_academico'].astype('category').cat.codes
    elif 'periodo_academico_info_sede' in df_long.columns: 
        df_long['periodo_academico_encoded'] = df_long['periodo_academico_info_sede'].astype('category').cat.codes
    else:
        df_long['periodo_academico_encoded'] = 0 

    print("   Generando Lags (Historial)...")
    grouper = df_long.groupby(['sede', 'sector_nombre'])['consumo_kwh']
    
    df_long['lag_1h'] = grouper.shift(1)
    df_long['lag_24h'] = grouper.shift(24)   
    df_long['lag_168h'] = grouper.shift(168)  
    
    df_long = df_long.dropna(subset=['lag_1h', 'lag_24h', 'lag_168h']).reset_index(drop=True)
    
    FEATURES = [
        'hour_sin', 'hour_cos', 'day_sin', 'day_cos', 'month_sin', 'month_cos',
        'es_dia_laboral', 'es_festivo', 'es_semana_parciales', 'es_semana_finales',
        
        'temperatura_exterior_c', 'ocupacion_pct',
        
        'sede_encoded', 'sector_encoded', 'periodo_academico_encoded',
        
        'lag_1h', 'lag_24h', 'lag_168h',
        
        'area_m2', 'num_estudiantes', 'altitud_msnm', 'tiene_laboratorios_pesados'
    ]
    TARGET = 'consumo_kwh'
    
    split_date = '2025-01-01'
    train = df_long[df_long['timestamp'] < split_date].copy()
    test = df_long[df_long['timestamp'] >= split_date].copy()
    
    print(f"4. Entrenando XGBoost Global ({train.shape[0]} registros de entrenamiento)...")
    
    model = xgb.XGBRegressor(
        n_estimators=1000,
        learning_rate=0.05,
        max_depth=9,
        early_stopping_rounds=50,
        n_jobs=-1,
        enable_categorical=True
    )
    
    model.fit(
        train[FEATURES], train[TARGET],
        eval_set=[(test[FEATURES], test[TARGET])],
        verbose=100
    )
    
    print("\n5. Evaluando y Detectando Anomalías por Sector...")
    
    test['prediccion'] = model.predict(test[FEATURES])
    
    test['error'] = test[TARGET] - test['prediccion']
    
    stats_por_sector = test.groupby('sector_nombre')['error'].agg(['mean', 'std']).reset_index()
    test = test.merge(stats_por_sector, on='sector_nombre', how='left')
    
    test['umbral_superior'] = test['mean'] + (2.5 * test['std'])
    test['es_pico_anomalo'] = test['error'] > test['umbral_superior']
    
    print("\n6. Analizando Ineficiencia Estructural (EUI - Energy Use Intensity)...")
    
    eui_analysis = test.groupby(['sede', 'sector_nombre']).agg(
        consumo_total=('consumo_kwh', 'sum'),
        consumo_predicho=('prediccion', 'sum'),
        area_m2=('area_m2', 'first'),
        horas_totales=('timestamp', 'count')
    ).reset_index()
    
    eui_analysis['intensidad_kwh_hora'] = eui_analysis['consumo_total'] / eui_analysis['horas_totales']
    eui_analysis['desperdicio_kwh'] = eui_analysis['consumo_total'] - eui_analysis['consumo_predicho']
    eui_analysis['%_desviaje'] = (eui_analysis['desperdicio_kwh'] / eui_analysis['consumo_predicho']) * 100
    
    print("\n=== RANKING DE SECTORES INEFICIENTES (Por Desviación Sistemática del Modelo) ===")
    inefficient_sectors = eui_analysis.sort_values('%_desviaje', ascending=False)
    
    display_cols = ['sede', 'sector_nombre', 'intensidad_kwh_hora', 'desperdicio_kwh', '%_desviaje']
    print(inefficient_sectors[display_cols].head(10))
    
    inefficiency_path = os.path.join(PLOTS_DIR, "ranking_sectores_ineficientes.csv")
    inefficient_sectors.to_csv(inefficiency_path, index=False)
    print(f"Reporte de ineficiencia guardado en: {inefficiency_path}")
    
    metrics_sector = []
    for sector in test['sector_nombre'].unique():
        subset = test[test['sector_nombre'] == sector]
        rmse = np.sqrt(mean_squared_error(subset[TARGET], subset['prediccion']))
        anomalias = subset['es_pico_anomalo'].sum()
        pct_anomalias = (anomalias / len(subset)) * 100
        
        metrics_sector.append({
            'Sector': sector,
            'RMSE (Error Promedio)': round(rmse, 2),
            'Total Anomalías Detectadas': anomalias,
            '% Anomalía': round(pct_anomalias, 2)
        })
        
    metrics_df = pd.DataFrame(metrics_sector)
    print(metrics_df)
    
    picos = test[test['es_pico_anomalo']].sort_values('error', ascending=False).head(5)
    print("\n--- Top 5 Picos Anómalos Críticos Detectados ---")
    if not picos.empty:
        print(picos[['timestamp', 'sede', 'sector_nombre', 'consumo_kwh', 'prediccion', 'error']])
    else:
        print("No se detectaron niveles extremos de anomalía en el set de prueba.")
        
    
    sector_plot = 'comedor' 
    plot_df = test[(test['sector_nombre'].str.contains(sector_plot)) & 
                   (test['timestamp'] >= '2025-03-01') & (test['timestamp'] < '2025-03-08')]
    
    if not plot_df.empty:
        fig = px.line(plot_df, x='timestamp', y=[TARGET, 'prediccion'], 
                      title=f'Detección de Anomalías: Sector {sector_plot} (Marzo 2025)',
                      color_discrete_map={TARGET: 'cyan', 'prediccion': 'orange'},
                      template='plotly_dark')
        
        anomalias_plot = plot_df[plot_df['es_pico_anomalo']]
        if not anomalias_plot.empty:
            fig.add_scatter(x=anomalias_plot['timestamp'], y=anomalias_plot[TARGET], 
                            mode='markers', marker=dict(color='red', size=10, symbol='x'),
                            name='Pico Anómalo Identificado')
            
        plot_path = os.path.join(PLOTS_DIR, "analisis_sector_comedor.html")
        fig.write_html(plot_path)
        print(f"Gráfico guardado en: {plot_path}")

    output_csv = os.path.join(PLOTS_DIR, "predicciones_sectores_anomalias.csv")
    test.to_csv(output_csv, index=False)
    print(f"Resultados completos guardados en: {output_csv}")

if __name__ == "__main__":
    train_model_multisector()
