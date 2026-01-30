import pandas as pd
import shap
import xgboost as xgb
import matplotlib.pyplot as plt
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "../../phase-1-exploration/data")
RESULTS_DIR = os.path.join(BASE_DIR, "../results")
os.makedirs(RESULTS_DIR, exist_ok=True)

def run_shap_analysis():
    print("Loading data for SHAP analysis...")
    try:
        df = pd.read_csv(os.path.join(DATA_DIR, "consumos_uptc_clean.csv"))
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # We need to retrain/load the model identical to Phase 1
        # For this script, we'll train a global model on a subset to generate the explanation quickly
        # as saving/loading pickles across phases without strict structure can be brittle.
        
        TARGET = 'energia_total_kwh'
        FEATURES = ['hour_sin', 'hour_cos', 'day_sin', 'day_cos', 'month_sin', 'month_cos', 
                'temperatura_exterior_c', 'ocupacion_pct']
        
        print(f"Training proxy model on {len(df)} rows...")
        model = xgb.XGBRegressor(n_estimators=100, max_depth=4)
        model.fit(df[FEATURES], df[TARGET])
        
        # SHAP Explainer
        print("Calculating SHAP values...")
        explainer = shap.Explainer(model)
        
        # Explain a subset (e.g., 500 random samples) for performance
        subset = df[FEATURES].sample(n=500, random_state=42)
        shap_values = explainer(subset)
        
        # 1. Summary Plot (Beeswarm)
        print("Generating Beeswarm plot...")
        plt.figure()
        shap.summary_plot(shap_values, subset, show=False)
        plt.tight_layout()
        plt.savefig(os.path.join(RESULTS_DIR, "shap_beeswarm.png"))
        plt.close()
        
        # 2. Bar Plot (Global Importance)
        print("Generating Importance plot...")
        plt.figure()
        shap.summary_plot(shap_values, subset, plot_type="bar", show=False)
        plt.tight_layout()
        plt.savefig(os.path.join(RESULTS_DIR, "shap_importance.png"))
        plt.close()
        
        print("\nSHAP Analysis Complete. Plots saved to phase-5-explainability/results/")
        
    except FileNotFoundError:
        print("Data not found.")

if __name__ == "__main__":
    run_shap_analysis()
