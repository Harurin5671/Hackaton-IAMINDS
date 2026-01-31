# Plan Phase 3.5: Advanced Recommendation Engine (Human-Centric)

## Problem
Current recommendations are "data-heavy" and technical. They lack the "so what?" factor needed for non-technical stakeholders (juries, managers).

## Objective
Transform raw anomaly data into **"Executive Action Cards"** that answer three simple questions:
1.  **What is happening?** (In plain Spanish).
2.  **How much is it costing me?** (Monetary impact).
3.  **What exactly should I do?** (Step-by-step instructions).

## Strategy: "The Expert Consultant" Prompt

We will upgrade the `02_llm_advisor.py` script to use a **Chain-of-Thought** prompting strategy with **Few-Shot Examples**.

### 1. New Prompt Architecture
*   **Persona**: You are not just an engineer, you are a **Strategic Energy Consultant** for a University.
*   **Tone**: Urgent, professional, but extremely clear. Avoid jargon like "MSE", "Residuals". Use "Waste", "Overconsumption".
*   **Structure**:
    *   **Headline**: Catchy and alarming (e.g., "⚠️ Money Leak Detected in Cafeteria").
    *   **Context**: "While the campus was empty (Sunday), the Cafeteria consumed energy as if it were full."
    *   **Impact**: "Estimated loss: **$200,000 COP** this week."
    *   **Action Plan**:
        *   [ ] Check industrial fridges seals.
        *   [ ] Verify if the oven cleaning cycle was left on.

### 2. Knowledge Injection
We will add a small "Fault Dictionary" to the context.
*   If *Sector=Kitchen* -> Suggest: Fridges, Ovens.
*   If *Sector=Classroom* -> Suggest: Lights, Projectors, A/C.
*   If *Sector=Labs* -> Suggest: Centrifuges, Compressors.

### 3. Implementation Steps
1.  **Modify `phase-3-recommendations/notebooks/02_llm_advisor.py`**:
    *   Update `PromptTemplate` with the new structures.
    *   Include a "Cost Estimator" logic (approx 800 COP/kWh) to feed the LLM real dollar signs.
2.  **Run the Script**: Regenerate the artifacts.
3.  **Validate**: Check `advisor_report.md` to see the difference.

## Key Success Metric
A person with ZERO engineering knowledge must understand exactly what is wrong just by reading the title and the first sentence.
