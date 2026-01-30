import pandas as pd
import numpy as np
try:
    import xgboost as xgb
    XGB_AVAILABLE = True
except ImportError:
    XGB_AVAILABLE = False
    print("XGBoost not found, falling back to RandomForest.")
except OSError:
    XGB_AVAILABLE = False
    print("XGBoost library load failed (likely libomp issue), falling back to RandomForest.")

from sklearn.ensemble import IsolationForest, RandomForestRegressor
import pickle
import os

def train_predictive_model(df):
    """
    Trains a model to predict energy consumption.
    Uses XGBoost if available, else RandomForest.
    """
    
    # Feature Engineering
    # Lag features are critical for time series, but complicate the "live" inference without history.
    # For this hackathon scope, we'll use a simple lag or just time features to keep it robust enough.
    
    # Let's use a 24h lag if available, but handle NaNs
    df['lag_24h'] = df.groupby(['sede', 'sector'])['consumption'].shift(24)
    
    # Drop initial rows where lag is NaN for training
    df_train = df.dropna(subset=['lag_24h'])
    
    features = ['hour', 'is_weekend', 'temp_ext', 'ocupacion', 'lag_24h']
    target = 'consumption'
    
    if XGB_AVAILABLE:
        print("Training predictive model (XGBoost)...")
        model = xgb.XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=5, random_state=42)
    else:
        print("Training predictive model (RandomForest)...")
        model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
        
    model.fit(df_train[features], df_train[target])
    
    # Predict on the whole set (filling lag with 0 or something for the first day is risky, 
    # but since we dropped them for training, let's predict only where we have data or handle it)
    # Ideally, we predict on df_train index, and for the full df we might miss the first 24h of predictions.
    
    # Fill NAs in lag for prediction just to get a value (or don't predict for them)
    # detailed: we can accept nans if model handles it (XGB does), RF doesn't usually.
    
    if not XGB_AVAILABLE:
        # RF doesn't handle NaNs by default
        df_for_pred = df.copy()
        df_for_pred['lag_24h'] = df_for_pred['lag_24h'].fillna(method='bfill').fillna(0)
        df['pred_consumption'] = model.predict(df_for_pred[features])
    else:
        df['pred_consumption'] = model.predict(df[features])
    
    # Calculate Residuals
    df['residual'] = df['consumption'] - df['pred_consumption']
    
    return model, df

def detect_anomalies(df):
    """
    Uses Isolation Forest to detect anomalies in consumption patterns.
    """
    print("Detecting anomalies (Isolation Forest)...")
    
    # We detect anomalies based on consumption and occupancy relationship
    iso = IsolationForest(contamination=0.02, random_state=42)
    
    # We need to handle NaNs if any
    df_clean = df[['consumption', 'ocupacion']].fillna(0)
    
    df['anomaly'] = iso.fit_predict(df_clean)
    
    # -1 is anomaly, 1 is normal
    return df

def save_models(xgb_model, iso_model, path='models'):
    os.makedirs(path, exist_ok=True)
    with open(f'{path}/xgb_model.pkl', 'wb') as f:
        pickle.dump(xgb_model, f)
    # Isolation forest is not returned as an object in the simple function above, 
    # but usually we'd train it and keep it. For now, we fit_predict every time or return it if needed.
    # Let's update detect_anomalies to return the model too if we want to save it.
    pass

if __name__ == "__main__":
    # Test run
    try:
        df = pd.read_csv("uptc_final.csv", parse_dates=True, index_col=0)
        model, df_pred = train_predictive_model(df)
        df_final = detect_anomalies(df_pred)
        print(df_final[['consumption', 'pred_consumption', 'anomaly']].tail())
        df_final.to_csv("uptc_processed.csv")
        print("Processed data saved to uptc_processed.csv")
    except FileNotFoundError:
        print("uptc_final.csv not found. Run data_generator.py first.")
