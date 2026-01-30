# Phase 5: Explainability (XAI) & Ethics

## Objective
Ensure the AI's decisions are transparent, auditable, and the impact is clearly quantified in environmental and economic terms.

## Strategy

### 1. Explainable AI (XAI)
We will use **SHAP (SHapley Additive exPlanations)** to interpret the XGBoost model from Phase 1.
*   **Global Interpretability**: Which features drive energy consumption the most? (e.g., Occupancy vs. Temperature).
*   **Local Interpretability**: Why did the model predict 500 kWh for *this specific hour*?

### 2. Impact Quantification
Calculate potential savings based on Phase 2's "Inefficiency Detection".
*   **Energy**: Total kWh saved if "Phantom Consumption" is eliminated.
*   **Environment**: CO2 reduction using the grid emission factor (0.164 kg CO2/kWh).
*   **Economy**: Savings in COP (Mean $800 COP/kWh).

### 3. Ethics & Transparency
*   **Model Card**: A standardized document explaining model limitations, training data, and intended use.
*   **Confidence Scores**: Displaying when the model is unsure.

## Implementation Plan

#### Step 1: SHAP Analysis (`01_shap_analysis.py`)
*   Load the Phase 1 XGBoost model.
*   Compute SHAP values for the Test set.
*   Generate Summary Plot (Beeswarm) and Dependence Plots.

#### Step 2: Impact Report (`02_impact_metrics.py`)
*   Load Phase 2 `waste_summary.csv`.
*   Convert kWh to CO2 and COP.
*   Generate `impact_dashboard.html`.

#### Step 3: Ethics Statement (`ethics_card.md`)
*   Write the transparency statement for the repository.

## Deliverables
*   `shap_summary_plot.png`
*   `impact_report.csv`
*   `ETHICS.md`
