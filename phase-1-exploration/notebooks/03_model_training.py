import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.metrics import mean_squared_error, mean_absolute_error
import plotly.express as px
import os

# --- CONFIGURACIÓN ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "../data")
PLOTS_DIR = os.path.join(BASE_DIR, "../docs/model_plots")
os.makedirs(PLOTS_DIR, exist_ok=True)

# Lista de columnas de sectores específicos
SECTOR_COLS = [
    'energia_comedor_kwh',
    'energia_salones_kwh', 
    'energia_laboratorios_kwh',
    'energia_auditorios_kwh',
    'energia_oficinas_kwh'
]

def train_model_multisector():
    print("--- INICIANDO ENTRENAMIENTO MULTI-SECTOR ---")
    
    # 1. Cargar Datos Limpios
    print("1. Cargando datos...")
    input_file = os.path.join(DATA_DIR, "consumos_uptc_clean.csv")
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"No se encontró el archivo {input_file}. Ejecuta 02_preprocessing.py primero.")
        
    df_consumos = pd.read_csv(input_file)
    df_sedes = pd.read_csv(os.path.join(DATA_DIR, "sedes_uptc.csv"))
    
    # Merge con información de sedes
    df = pd.merge(df_consumos, df_sedes, on='sede_id', how='left', suffixes=('', '_info_sede'))
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Corrección de Tipos de Datos (Booleanos a Int) para XGBoost
    bool_cols_to_fix = ['tiene_laboratorios_pesados', 'es_festivo', 'es_semana_parciales', 'es_semana_finales', 'tiene_residencias']
    for col in bool_cols_to_fix:
        if col in df.columns:
            # Forzar conversión a numérico 0/1
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

    # 2. TRANSFORMACIÓN A FORMATO LARGO (Melt)
    # Convertimos las columnas de sectores en filas -> [timestamp, sede, sector, consumo]
    print("2. Transformando a formato Largo (Sectores)...")
    
    # Identificar columnas base (que no son de energía específica)
    base_cols = ['timestamp', 'sede', 'sede_id', 'temperatura_exterior_c', 'ocupacion_pct', 
                 'dia_semana', 'es_festivo', 'es_semana_parciales', 'es_semana_finales',
                 'area_m2', 'num_estudiantes', 'altitud_msnm', 'tiene_laboratorios_pesados']
    
    # Asegurarnos de tener columnas base existentes
    base_cols = [c for c in base_cols if c in df.columns]
    
    df_long = df.melt(
        id_vars=base_cols,
        value_vars=SECTOR_COLS,
        var_name='sector_nombre',
        value_name='consumo_kwh'
    )
    
    # Limpieza básica del nombre del sector (ej: 'energia_comedor_kwh' -> 'comedor')
    df_long['sector_nombre'] = df_long['sector_nombre'].str.replace('energia_', '').str.replace('_kwh', '')
    
    print(f"   Datos transformados. Filas: {len(df_long)}. Sectores únicos: {df_long['sector_nombre'].unique()}")

    # 3. FEATURE ENGINEERING AVANZADO
    print("3. Generando Features...")
    df_long = df_long.sort_values(['sede', 'sector_nombre', 'timestamp'])
    
    # 1. Dia Laboral (Lun-Vie)
    df_long['es_dia_laboral'] = df_long['timestamp'].dt.dayofweek.isin([0,1,2,3,4]).astype(int)

    # 2. Features Temporales Cíclicas
    df_long['hour_sin'] = np.sin(2 * np.pi * df_long['timestamp'].dt.hour / 24)
    df_long['hour_cos'] = np.cos(2 * np.pi * df_long['timestamp'].dt.hour / 24)
    df_long['day_sin'] = np.sin(2 * np.pi * df_long['timestamp'].dt.dayofweek / 7)
    df_long['day_cos'] = np.cos(2 * np.pi * df_long['timestamp'].dt.dayofweek / 7)
    df_long['month_sin'] = np.sin(2 * np.pi * df_long['timestamp'].dt.month / 12)
    df_long['month_cos'] = np.cos(2 * np.pi * df_long['timestamp'].dt.month / 12)
    
    # 3. Encoding Variables Categóricas
    df_long['sector_encoded'] = df_long['sector_nombre'].astype('category').cat.codes
    df_long['sede_encoded'] = df_long['sede'].astype('category').cat.codes
    
    # Corregir existencia de periodo_academico, si no está en el dataframe, crearlo o ignorarlo con seguridad
    if 'periodo_academico' in df_long.columns: 
        df_long['periodo_academico_encoded'] = df_long['periodo_academico'].astype('category').cat.codes
    elif 'periodo_academico_info_sede' in df_long.columns: # Posible nombre post-merge
        df_long['periodo_academico_encoded'] = df_long['periodo_academico_info_sede'].astype('category').cat.codes
    else:
        df_long['periodo_academico_encoded'] = 0 # Valor dummy si falta

    # 4. Features de Lags (Retrasos) - CLAVE: Agrupado por Sede Y Sector
    # El consumo de ayer a esta hora, pero ESPECIFICAMENTE de este sector
    print("   Generando Lags (Historial)...")
    grouper = df_long.groupby(['sede', 'sector_nombre'])['consumo_kwh']
    
    df_long['lag_1h'] = grouper.shift(1)
    df_long['lag_24h'] = grouper.shift(24)    # Mismo sector, ayer misma hora
    df_long['lag_168h'] = grouper.shift(168)  # Mismo sector, semana pasada
    
    # Eliminar nulos por lags
    df_long = df_long.dropna(subset=['lag_1h', 'lag_24h', 'lag_168h']).reset_index(drop=True)
    
    # 5. DEFINIR MODELO (LISTA COMPLETA RESTAURADA)
    FEATURES = [
        # Time & Cycles
        'hour_sin', 'hour_cos', 'day_sin', 'day_cos', 'month_sin', 'month_cos',
        'es_dia_laboral', 'es_festivo', 'es_semana_parciales', 'es_semana_finales',
        
        # Environmental / Occupancy
        'temperatura_exterior_c', 'ocupacion_pct',
        
        # Categorical IDs
        'sede_encoded', 'sector_encoded', 'periodo_academico_encoded',
        
        # Lags
        'lag_1h', 'lag_24h', 'lag_168h',
        
        # Static Facilities Info
        'area_m2', 'num_estudiantes', 'altitud_msnm', 'tiene_laboratorios_pesados'
    ]
    TARGET = 'consumo_kwh'
    
    # Split Train/Test (Por fecha)
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
    
    # 5. EVALUACIÓN Y DETECCIÓN DE PICOS ANÓMALOS
    print("\n5. Evaluando y Detectando Anomalías por Sector...")
    
    # Predecir
    test['prediccion'] = model.predict(test[FEATURES])
    
    # Calcular Error (Residuo)
    test['error'] = test[TARGET] - test['prediccion']
    
    # Definir umbral de anomalía dinámica por sector
    # Una anomalía es cuando el error es > 2 desviaciones estándar del error típico de ese sector
    stats_por_sector = test.groupby('sector_nombre')['error'].agg(['mean', 'std']).reset_index()
    test = test.merge(stats_por_sector, on='sector_nombre', how='left')
    
    # Lógica de Pico Anómalo: El valor real es mucho mayor al predicho (Residuo positivo grande)
    # Usamos (Media + 2*Std) como límite superior
    test['umbral_superior'] = test['mean'] + (2.5 * test['std'])
    test['es_pico_anomalo'] = test['error'] > test['umbral_superior']
    
    # --- 6. ANÁLISIS AVANZADO: SECTORES INEFICIENTES (EUI) ---
    print("\n6. Analizando Ineficiencia Estructural (EUI - Energy Use Intensity)...")
    
    # 6.1 Calcular consumo promedio real vs predicho por Sector
    eui_analysis = test.groupby(['sede', 'sector_nombre']).agg(
        consumo_total=('consumo_kwh', 'sum'),
        consumo_predicho=('prediccion', 'sum'),
        area_m2=('area_m2', 'first'), # Asumimos área fija por sede (simplificación válida para este nivel)
        horas_totales=('timestamp', 'count')
    ).reset_index()
    
    # Ajuste: El área en el dataset original es TOTAL de la sede. 
    # Para ser precisos, deberíamos tener área por sector. 
    # Como aproximación para detectar "Ineficiencia Relativa", usaremos el consumo intensivo (kWh/hora de operación).
    
    eui_analysis['intensidad_kwh_hora'] = eui_analysis['consumo_total'] / eui_analysis['horas_totales']
    eui_analysis['desperdicio_kwh'] = eui_analysis['consumo_total'] - eui_analysis['consumo_predicho']
    eui_analysis['%_desviaje'] = (eui_analysis['desperdicio_kwh'] / eui_analysis['consumo_predicho']) * 100
    
    # 6.2 Ranking de Ineficiencia
    # Un sector es "Ineficiente" si sistematícamente consume más de lo predicho (Desvío positivo alto)
    print("\n=== RANKING DE SECTORES INEFICIENTES (Por Desviación Sistemática del Modelo) ===")
    inefficient_sectors = eui_analysis.sort_values('%_desviaje', ascending=False)
    
    # Formatear para visualización
    display_cols = ['sede', 'sector_nombre', 'intensidad_kwh_hora', 'desperdicio_kwh', '%_desviaje']
    print(inefficient_sectors[display_cols].head(10))
    
    # Guardar reporte de ineficiencia
    inefficiency_path = os.path.join(PLOTS_DIR, "ranking_sectores_ineficientes.csv")
    inefficient_sectors.to_csv(inefficiency_path, index=False)
    print(f"Reporte de ineficiencia guardado en: {inefficiency_path}")

    # --- REPORTE DE RESULTADOS PREVIOS ---
    print("\n=== REPORTE DE ANOMALÍAS POR SECTOR (Test Data 2025) ===")
    
    # 1. Precisión general por sector
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
    
    # 2. Ejemplo de Picos Detectados
    picos = test[test['es_pico_anomalo']].sort_values('error', ascending=False).head(5)
    print("\n--- Top 5 Picos Anómalos Críticos Detectados ---")
    if not picos.empty:
        print(picos[['timestamp', 'sede', 'sector_nombre', 'consumo_kwh', 'prediccion', 'error']])
    else:
        print("No se detectaron niveles extremos de anomalía en el set de prueba.")
        
    # 3. Guardar Análisis Visual
    # Graficar un sector específico para ver la anomalía (ej: Comedor)
    print("\nGenerando gráfico de validación para 'Comedor'...")
    sector_plot = 'comedor' # Ajustar si el nombre cambia tras el replace
    plot_df = test[(test['sector_nombre'].str.contains(sector_plot)) & 
                   (test['timestamp'] >= '2025-03-01') & (test['timestamp'] < '2025-03-08')] # Una semana de ejemplo
    
    if not plot_df.empty:
        fig = px.line(plot_df, x='timestamp', y=[TARGET, 'prediccion'], 
                      title=f'Detección de Anomalías: Sector {sector_plot} (Marzo 2025)',
                      color_discrete_map={TARGET: 'cyan', 'prediccion': 'orange'},
                      template='plotly_dark')
        
        # Marcar anomalias con puntos rojos
        anomalias_plot = plot_df[plot_df['es_pico_anomalo']]
        if not anomalias_plot.empty:
            fig.add_scatter(x=anomalias_plot['timestamp'], y=anomalias_plot[TARGET], 
                            mode='markers', marker=dict(color='red', size=10, symbol='x'),
                            name='Pico Anómalo Identificado')
            
        plot_path = os.path.join(PLOTS_DIR, "analisis_sector_comedor.html")
        fig.write_html(plot_path)
        print(f"Gráfico guardado en: {plot_path}")

    # Guardar CSV con predicciones y flags de anomalía
    output_csv = os.path.join(PLOTS_DIR, "predicciones_sectores_anomalias.csv")
    test.to_csv(output_csv, index=False)
    print(f"Resultados completos guardados en: {output_csv}")

if __name__ == "__main__":
    train_model_multisector()
