# Phase 4: Interface & User Experience

## Objective
Create an interactive Dashboard that consolidates all insights (Prediction, Anomalies, Recommendations) and provides a Natural Language Interface (Chatbot) for facility managers.

## Technology Stack
*   **Frontend/Backend**: Streamlit (Python).
*   **Search/Chat**: LangChain + Groq (Llama-3).
*   **Visualizations**: Plotly Express.

## Architecture

### 1. Data Integration
The app will ingest outputs from previous phases:
*   `consumos_uptc_clean.csv` (General Trends).
*   `anomalies_detected.csv` (Red flags).
*   `advisor_report.md` (AI Recommendations).

### 2. Modules

#### Module A: The "Command Center" (KPIs)
*   **Metric 1**: Total Consumption vs. Predicted (Real-time efficiency).
*   **Metric 2**: Active Anomalies (Count).
*   **Metric 3**: Estimated Waste Cost (COP).

#### Module B: Interactive Analytics
*   **Time Series**: Filter by Sede, Sector, Date Range.
*   **Anomaly Map**: Scatter plot highlighting "Red" zones (Phase 2).

#### Module C: The AI Assistant (XAI)
*   **Functionality**: Query the data using natural language.
*   **Examples**:
    *   "Show me the consumption pattern of Comedores."
    *   "Why is Tunja red today?"
*   **Implementation**: A LangChain Agent with access to the `pandas` dataframe and the `recommendations` text.

## Implementation Plan

#### Step 1: App Skeleton (`dashboard.py`)
*   Setup Streamlit layout (Sidebar, Tabs).
*   Load Data functions.

#### Step 2: Visualization Components
*   Implement Plotly charts for Phase 1 & 2 data.

#### Step 3: Chatbot Integration
*   Embed the `ChatGroq` agent.
*   Give it context of the "Advisor Report" (Phase 3).

## Deliverables
*   `dashboard.py`: The executable app.
*   `run_dashboard.sh`: Helper script.
