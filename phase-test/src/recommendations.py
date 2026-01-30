import pandas as pd

def generate_recommendations(row):
    """
    Generates a recommendation based on a single row of data (with anomalies/residuals).
    """
    recs = []
    
    # Inefficiency: High consumption with low occupancy
    # Assuming 'residual' > X means consumption is much higher than predicted/expected
    # Or simply Logic: Low Occupancy (<10) but High Consumption (> threshold)
    
    # We can use the 'residual' from the ML model. 
    # If residual is positive and large, we consumed more than expected.
    
    if row.get('residual', 0) > 10: 
        recs.append("Consumo inusualmente alto detectado. Verificar equipos encendidos innecesariamente.")
        
    if row['anomaly'] == -1:
         recs.append("Patrón anómalo detectado por el sistema de IA. Revisión manual recomendada.")
         
    if row['ocupacion'] < 10 and row['consumption'] > 50: # Thresholds need tuning based on data scale
        recs.append(f"Ineficiencia crítica: Sede vacía ({row['ocupacion']} personas) con alto consumo ({row['consumption']:.2f} kWh).")
        
    if row['hour'] >= 22 or row['hour'] <= 5:
        if row['consumption'] > 20:
            recs.append("Alto consumo nocturno. Verificar programación de luces o climatización.")

    return " | ".join(recs) if recs else "Operación normal"

def analyze_inefficiencies(df):
    """
    Applies logic to detect inefficiencies across the dataframe.
    """
    print("Generating recommendations...")
    df['recommendation'] = df.apply(generate_recommendations, axis=1)
    return df
