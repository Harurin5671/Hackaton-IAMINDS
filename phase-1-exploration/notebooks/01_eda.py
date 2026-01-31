import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "../data")
OUTPUT_DIR = os.path.join(BASE_DIR, "../docs/eda_plots")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_data():
    print("Loading data...")
    try:
        csv_path = os.path.join(DATA_DIR, "consumos_uptc.csv")
        df = pd.read_csv(csv_path)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        print(f"Data loaded: {df.shape}")
        return df
    except FileNotFoundError:
        print(f"Error: {csv_path} not found.")
        return None

def check_quality(df):
    print("\n--- Data Quality Check ---")
    
    missing = df.isnull().sum()
    missing = missing[missing > 0]
    print(f"Missing Values:\n{missing}")
    
    cols_energy = [c for c in df.columns if 'energia' in c or 'kwh' in c]
    for col in cols_energy:
        neg_count = (df[col] < 0).sum()
        if neg_count > 0:
            print(f"⚠️ Warning: {neg_count} negative values in {col}")

    dupes = df.duplicated().sum()
    print(f"Duplicate Rows: {dupes}")

def plot_total_consumption(df):
    print("\nPlotting Total Consumption per Sede...")
    df_daily = df.groupby(['sede', pd.Grouper(key='timestamp', freq='D')])['energia_total_kwh'].sum().reset_index()
    
    fig = px.line(df_daily, x='timestamp', y='energia_total_kwh', color='sede', 
                  title='Daily Total Energy Consumption by Sede')
    fig.write_html(os.path.join(OUTPUT_DIR, "total_consumption_daily.html"))
    print("Saved total_consumption_daily.html")

def plot_sector_distribution(df):
    print("\nPlotting Sector Distribution...")
    sector_cols = [c for c in df.columns if 'energia_' in c and c != 'energia_total_kwh']
    
    df_melt = df.melt(id_vars=['sede', 'timestamp'], value_vars=sector_cols, 
                      var_name='Sector', value_name='Consumption_kWh')
    
    df_melt['Sector'] = df_melt['Sector'].str.replace('energia_', '').str.replace('_kwh', '')
    
    fig = px.box(df_melt, x='sede', y='Consumption_kWh', color='Sector', 
                 title='Distribution of Hourly Consumption by Sector and Sede')
    fig.write_html(os.path.join(OUTPUT_DIR, "sector_distribution_boxplot.html"))
    print("Saved sector_distribution_boxplot.html")

def analyze_correlations(df):
    print("\nAnalyzing Correlations...")
    cols = ['energia_total_kwh', 'temperatura_exterior_c', 'ocupacion_pct', 'co2_kg']
    cols += [c for c in df.columns if 'energia_' in c and c != 'energia_total_kwh']
    
    corr = df[cols].corr()
    
    fig = px.imshow(corr, text_auto=True, title='Correlation Matrix')
    fig.write_html(os.path.join(OUTPUT_DIR, "correlation_matrix.html"))
    print("Saved correlation_matrix.html")

if __name__ == "__main__":
    df = load_data()
    if df is not None:
        check_quality(df)
        plot_total_consumption(df)
        plot_sector_distribution(df)
        analyze_correlations(df)
        print("\nEDA Completed. Check 'phase-1-exploration/docs/eda_plots' for results.")
