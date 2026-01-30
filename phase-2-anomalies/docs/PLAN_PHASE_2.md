# Phase 2: Anomaly Detection & Inefficiency Patterns

## Objective
Automatically identify situations of energy waste, inefficient operational patterns, and unusual outliers in the UPTC campuses.

## Strategy
We will use a hybrid approach combining **Unsupervised Machine Learning** and **Rule-Based Heuristics**.

### 1. Approaches

#### A. AI-Based Detection (Isolation Forest)
*   **Goal**: Find outliers that deviate significantly from the "normal" multivariate distribution.
*   **Algorithm**: Isolation Forest.
*   **Features**: `consumption`, `hour`, `dayofweek`, `ocupacion_pct`, `temperature`.
*   **Use Case**: Detecting unexplained spikes or drops (e.g., equipment failure, leaks).

#### B. Model-Based Residual Analysis
*   **Goal**: leverage the Phase 1 Prediction Model.
*   **Logic**: If `Actual Consumption` >> `Predicted Consumption`, it suggests an anomaly where energy is being used without a standard justification (weather/occupancy).
*   **Metric**: `Residual = Actual - Predicted`. Threshold: > 2 Standard Deviations.

#### C. Rule-Based Inefficiency (Domain Knowledge)
*   **Goal**: Detect known "bad practices".
*   **Rules**:
    1.  **"Phantom Consumption"**: High consumption when `ocupacion_pct` is near 0.
    2.  **Nighttime Waste**: High consumption in academic sectors (Salones, Auditorios) between 10 PM - 5 AM.
    3.  **Weekend Operations**: Office/Classroom consumption remaining high on Sundays.

### 2. Implementation Plan

#### Step 1: Anomaly Detection Script (`01_detect_anomalies.py`)
*   Load clean data from Phase 1.
*   Train Isolation Forest per Sede/Sector.
*   Calculate Residuals from Phase 1 XGBoost model.
*   Output: `anomalies.csv` with flagged rows.

#### Step 2: Inefficiency Analysis Script (`02_analyze_inefficiencies.py`)
*   Apply the specific rules (Phantom, Nighttime).
*   Quantify "Wasted Energy" (kWh) for these events.
*   Generate specific alerts (e.g., "Tunja Classrooms consumed 500kWh on Sunday").

#### Step 3: Visualization
*   Scatter plots highlighting anomalies in Red.
*   Heatmap of "Waste Intensity" by Hour vs. Day.

## Deliverables
*   `01_detect_anomalies.py` (Script)
*   `02_analyze_inefficiencies.py` (Script)
*   `anomalies_report.html` (Visualization)
*   `waste_summary.csv` (Quantified impact)
