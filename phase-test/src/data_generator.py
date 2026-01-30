import pandas as pd
import numpy as np

def generate_uptc_data():
    """
    Generates synthetic energy consumption data for UPTC sedes.
    
    Sedes: Tunja, Duitama, Sogamoso, Chiquinquirá
    Sectores: Comedores, Salones, Laboratorios, Auditorios, Oficinas
    Time range: 2018-01-01 to 2025-12-31
    
    Returns:
        pd.DataFrame: DataFrame containing the generated data.
    """
    # Sedes and their estimated base load (in fictional units or proportional to size)
    sedes = {'Tunja': 18000, 'Duitama': 5500, 'Sogamoso': 6000, 'Chiquinquirá': 2000}
    
    # Sectores required by the challenge
    sectores = ['Comedores', 'Salones', 'Laboratorios', 'Auditorios', 'Oficinas']
    
    # Historical range
    dates = pd.date_range(start="2018-01-01", end="2025-12-31", freq="h")
    
    data_list = []
    
    print(f"Generating data for {len(sedes)} sedes and {len(sectores)} sectors over {len(dates)} hours...")
    
    for sede, est in sedes.items():
        for sector in sectores:
            df = pd.DataFrame(index=dates)
            df['sede'] = sede
            df['sector'] = sector
            df['hour'] = df.index.hour
            # Weekend flag (Saturday=5, Sunday=6)
            df['is_weekend'] = (df.index.dayofweek >= 5).astype(int)
            
            # Synthetic external temperature (seasonal variation)
            # 12 degrees avg, +/- 8 degrees variation over the year
            day_of_year = df.index.dayofyear
            df['temp_ext'] = 12 + 8 * np.sin((day_of_year / 365) * 2 * np.pi)
            
            # Add some daily temperature variation
            df['temp_ext'] += 3 * np.sin((df['hour'] - 6) * 2 * np.pi / 24)
            
            # Base consumption logic
            base = est * 0.004
            
            # Sector-specific peak multipliers
            pico = 1.2
            if sector == 'Comedores':
                pico = 4.5  # High peak during lunch
            elif sector == 'Laboratorios':
                pico = 2.0  # Equipment usage
            
            # Hourly consumption pattern
            # Peak activity typically around 13:00 for comedores, or general day hours
            daily_pattern = np.exp(-((df['hour'] - 13)**2) / 6)
            
            # Reduce consumption on weekends/nights
            activity_factor = np.where(df['is_weekend'] == 1, 0.3, 1.0)
            
            # Random noise
            noise = np.random.normal(0, 1, len(df))
            
            # Calculate final consumption
            df['consumption'] = base * (1 + pico * daily_pattern * activity_factor) + noise
            
            # Ensure no negative consumption
            df['consumption'] = df['consumption'].clip(lower=0)
            
            # Occupancy (simulated)
            # High occupancy between 8 and 18, low otherwise
            df['ocupacion'] = np.where(
                df['hour'].between(8, 18), 
                np.random.randint(50, 90, len(df)), 
                5
            )
            df['ocupacion'] = df['ocupacion'] * activity_factor # Lower occupancy on weekends
            
            data_list.append(df)
            
    # Concatenate all data
    df_total = pd.concat(data_list).sort_index()
    return df_total

if __name__ == "__main__":
    df = generate_uptc_data()
    print(f"Generated {len(df)} rows.")
    print(df.head())
    df.to_csv("uptc_final.csv", index=True)
    print("Saved to uptc_final.csv")
