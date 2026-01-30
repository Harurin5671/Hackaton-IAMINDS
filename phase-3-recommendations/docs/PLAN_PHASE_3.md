# Phase 3: Intelligent Recommendation Engine

## Objective
Translate the anomalies and inefficiencies detected in Phase 2 into actionable, human-readable recommendations for facility managers.

## Strategy: Hybrid Engine (Rules + LLM)

We will combine deterministic rules (for accuracy) with Generative AI (for explainability and context).

### 1. Inputs (from Phase 2)
*   `anomalies_detected.csv`: Timestamps and locations of critical anomalies.
*   `waste_summary.csv`: Quantified "Phantom Consumption" events.

### 2. Architecture

#### A. The Trigger Layer (Rule Engine)
Classifies the type of anomaly into a "Scenario":
1.  **Scene 1: "The Phantom"** (High Energy / Low Occupancy).
2.  **Scene 2: "Night Owl"** (Academic usage at 3 AM).
3.  **Scene 3: "Peak Breaker"** (Exceeding max power capacity).
4.  **Scene 4: "Cooling Leak"** (High correlation with Temp but unexpected magnitude).

#### B. The Generator Layer (LLM - Groq/Llama3)
Takes the Scenario metadata and generates a "Notification Card".
*   **Prompt**: "You are an Energy Manager. Sector {sector} in {sede} consumed {kwh} kWh (20% above normal) during {hour}:00. Occupancy was {occ}%. Suggest specific maintenance actions regarding [Lighting, HVAC, Equipment]."
*   **Output**: Natural language advice.

### 3. Implementation Plan

#### Step 1: Recommendation Logic (`01_recommendation_logic.py`)
*   Load Phase 2 results.
*   Group anomalies by day/sector top prioritize the biggest "offenders".
*   Assign a `ScenarioID` to each cluster of anomalies.

#### Step 2: LLM Generator (`02_llm_advisor.py`)
*   Use `langchain-groq`.
*   Iterate through the top 5 most critical daily events.
*   Generate a detailed report for each.
*   **Fallback**: If API is offline, use robust string templates.

## Deliverables
*   `recommendations_log.csv`: Structured table of actions.
*   `advisor_report.md`: AI-generated daily briefing.
