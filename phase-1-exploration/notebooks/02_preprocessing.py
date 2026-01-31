import pandas as pd
import numpy as np
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "../data")
OUTPUT_FILE = os.path.join(DATA_DIR, "consumos_uptc_clean.csv")

def feature_engineering(df):
    df['hour'] = df['timestamp'].dt.hour
    df['dayofweek'] = df['timestamp'].dt.dayofweek
    df['month'] = df['timestamp'].dt.month
    
    df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
    df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
    
    df['day_sin'] = np.sin(2 * np.pi * df['dayofweek'] / 7)
    df['day_cos'] = np.cos(2 * np.pi * df['dayofweek'] / 7)
    
    df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
    df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
    
    return df

def clean_data(df):
    
    cols_energy = [c for c in df.columns if 'energia' in c or 'kwh' in c]
    for col in cols_energy:
        if (df[col] < 0).any():
            print(f"  Clipping negative values in {col}")
            df[col] = df[col].clip(lower=0)
            
    df = df.sort_values(by=['sede', 'timestamp'])
    
    numeric_cols = ['energia_total_kwh', 'energia_comedor_kwh', 'energia_salones_kwh', 
                    'energia_laboratorios_kwh', 'energia_auditorios_kwh', 'energia_oficinas_kwh',
                    'temperatura_exterior_c', 'ocupacion_pct', 'co2_kg', 'agua_litros']
    
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df.groupby('sede')[col].transform(lambda x: x.interpolate(method='linear', limit_direction='both'))
            
            if df[col].isnull().sum() > 0:
                print(f"  Filling remaining NaNs in {col} with 0")
                df[col] = df[col].fillna(0)
                
    return df

def main():
    try:
        csv_path = os.path.join(DATA_DIR, "consumos_uptc.csv")
        df = pd.read_csv(csv_path)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        df = clean_data(df)
        df = feature_engineering(df)
        
        df.to_csv(OUTPUT_FILE, index=False)
        print(f"Clean data saved to: {OUTPUT_FILE}")
        print(f"Shape: {df.shape}")
        
    except FileNotFoundError as e:
        print(e)

if __name__ == "__main__":
    main()
