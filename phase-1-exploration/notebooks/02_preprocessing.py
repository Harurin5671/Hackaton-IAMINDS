import pandas as pd
import numpy as np
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "../data")
OUTPUT_FILE = os.path.join(DATA_DIR, "consumos_uptc_clean.csv")

def feature_engineering(df):
    print("Engineering features...")
    # Cyclic Time Features
    df['hour'] = df['timestamp'].dt.hour
    df['dayofweek'] = df['timestamp'].dt.dayofweek
    df['month'] = df['timestamp'].dt.month
    
    df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
    df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
    
    df['day_sin'] = np.sin(2 * np.pi * df['dayofweek'] / 7)
    df['day_cos'] = np.cos(2 * np.pi * df['dayofweek'] / 7) # Correction: 7 days
    
    df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
    df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
    
    return df

def clean_data(df):
    print("Cleaning data...")
    
    # 1. Handle Negative Energy
    cols_energy = [c for c in df.columns if 'energia' in c or 'kwh' in c]
    for col in cols_energy:
        if (df[col] < 0).any():
            print(f"  Clipping negative values in {col}")
            df[col] = df[col].clip(lower=0)
            
    # 2. Sort
    df = df.sort_values(by=['sede', 'timestamp'])
    
    # 3. Imputation (Interpolation for continuous vars)
    # We interpolate within each 'sede' group to avoid jumping across sedes
    # However, doing it strictly by group is safer.
    
    numeric_cols = ['energia_total_kwh', 'energia_comedor_kwh', 'energia_salones_kwh', 
                    'energia_laboratorios_kwh', 'energia_auditorios_kwh', 'energia_oficinas_kwh',
                    'temperatura_exterior_c', 'ocupacion_pct', 'co2_kg', 'agua_litros']
    
    for col in numeric_cols:
        if col in df.columns:
            # Linear interpolation for time series gaps
            df[col] = df.groupby('sede')[col].transform(lambda x: x.interpolate(method='linear', limit_direction='both'))
            
            # Fill remaining NaNs with 0 (if valid) or Group Mean
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
        
        # Save
        df.to_csv(OUTPUT_FILE, index=False)
        print(f"Clean data saved to: {OUTPUT_FILE}")
        print(f"Shape: {df.shape}")
        
    except FileNotFoundError as e:
        print(e)

if __name__ == "__main__":
    main()
