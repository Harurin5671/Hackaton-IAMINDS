# Phase 1: Exploration & Predictive Modeling Plan

## Objective
Develop a predictive model for energy consumption in UPTC sedes, broken down by sectors (Comedores, Salones, Laboratorios, Auditorios, Oficinas), and identify opportunities for optimization.

## Dataset
- **Source**: `consumos_uptc.csv`
- **Period**: 2018-2025 (Hourly)
- **Key Variables**: `energia_total_kwh`, `energia_[sector]_kwh`, `ocupacion_pct`, `temperatura_exterior_c`, `co2_kg`.
- **Known Issues**: Missing values, outliers, inconsistencies in `periodo_academico` (as noted in Codebook).

## Step-by-Step Plan

### 1. Data Loading & Quality Check
- Load `consumos_uptc.csv`.
- **Validation**:
    - Check for missing values in critical columns (`energia_*`, `co2_kg`).
    - Identify anomalies/outliers (e.g., negative consumption, extreme spikes).
    - Consistency check for `periodo_academico` and timestamps.

### 2. Exploratory Data Analysis (EDA)
- **Visualizations**:
    - Time series plots of total consumption per Sede.
    - Daily profiles by Sector (e.g., Comedores peak at noon?).
    - Correlation heatmap (Temperature vs. Consumption).
    - Boxplots for weekend vs. weekday consumption.
- **Goal**: Understand the baseline behavior and spot the "intentional quality problems".

### 3. Preprocessing & Feature Engineering
- **Imputation**: Handle missing data (interpolate for short gaps, use average profiles for longer gaps).
- **Feature Creation**:
    - Cyclic features for Hour, Day of Week, Month (`sin_hour`, `cos_hour`).
    - Lag features (previous 24h consumption).
    - Rolling averages (7-day window).
    - "Is Special Day" (Holiday/Exam week).

### 4. Predictive Modeling
- **Target**: `energia_[sector]_kwh` (Multi-output or separate models).
- **Models to Pilot**:
    - **Baseline**: Historical Average.
    - **XGBoost**: Tree-based model handling non-linear relationships with exogenous variables (temp, occupancy).
    - **Prophet** (Optional): If strong seasonality is observed and less reliance on exogenous features is preferred.
- **Training Split**: Train (2018-2023), Validation (2024), Test (2025).

### 5. Evaluation
- **Metrics**: RMSE (Root Mean Squared Error), MAE (Mean Absolute Error).
- **Analysis**: Error distribution by 'Sector' to see which areas are hardest to predict.

## Deliverables
- `01_eda.py`: Script to generate inspection reports and plots.
- `02_preprocessing.py`: pipeline to clean data.
- `03_model_training.py`: Training script for XGBoost.
- `model_metrics.md`: Report on model performance.
