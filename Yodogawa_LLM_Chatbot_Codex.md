# Yodogawa Matching Score Project — LLM Chatbot Integration Spec

## Purpose
This document describes how to turn the existing notebook-based **Yodogawa apartment matching project** into an **LLM-powered chatbot application**.

The chatbot should use the **trained XGBoost model as the ranking engine** and use the **LLM only as the conversational interface**.

The goal is to let a user say things like:

> I want a 1LDK under 95,000 yen near Shin-Osaka, within 10 minutes from the station.

and receive:
- extracted preferences,
- model-based ranking,
- Top-5 property recommendations,
- natural-language explanations grounded in real model outputs.

---

## Core Principle
Do **not** replace the trained model with the LLM.

Use this separation of responsibilities:

- **LLM**
  - understands user messages,
  - extracts apartment preferences,
  - asks follow-up questions when necessary,
  - explains results naturally.

- **Matching model (XGBoost)**
  - scores listings,
  - ranks apartments,
  - returns Top-5 recommendations.

This ensures recommendations remain **deterministic, score-based, and grounded in project data**.

---

## Existing Project Context
Current notebook pipeline:

```text
src/
  data/
    suumo_raw_data.csv
    yodogawa_data_cleaning.csv
    yodogawa_feature_eng.csv
  model/
    yodogawa_match_model.pkl
  yodogawa_data_cleaning.ipynb
  yodogawa_feature_eng.ipynb
  yodogawa_train_model.ipynb
  yodogawa_predict_matching_score.ipynb
  yodogawa_recommendation_top5.ipynb
```

### Current flow
1. Clean raw listing data.
2. Build engineered features.
3. Train XGBoost model.
4. Predict matching scores.
5. Return Top-5 properties.

### Important constraints
- The current implementation is notebook-based.
- Paths currently use Windows-style relative paths.
- Large data/model files are excluded by default.
- Python 3.13 is currently used.

---

## Target Outcome
Build an application that supports this flow:

```text
User -> LLM chatbot -> preference extraction -> recommendation service -> model scoring -> Top-5 results -> LLM response
```

The chatbot should:
- collect user preferences through natural conversation,
- call a backend function or API,
- receive ranked results from the trained model,
- present those results in clear Japanese or English natural language.

---

## Recommended Architecture

```text
frontend/chat UI
    |
    v
LLM orchestration layer
    |
    +--> preference extraction
    |
    +--> tool/function call: recommend_yodogawa_apartments(...)
              |
              v
        recommender service
              |
              +--> load listings
              +--> engineer inference features
              +--> load trained XGBoost model
              +--> compute matching scores
              +--> return Top-5 + explanation flags
```

### Key design rule
The **inference-time feature engineering** must match the **training-time feature engineering** exactly.

If training used a certain column order, category mapping, missing-value rule, or derived feature, the same logic must be reused during chatbot inference.

---

## Refactor Plan
The notebooks should remain available for exploration, but the chatbot must use normal Python modules.

### Suggested application structure

```text
app/
  __init__.py
  api.py
  chat_agent.py
  recommender.py
  feature_pipeline.py
  schemas.py
  config.py
src/
  data/
  model/
  yodogawa_data_cleaning.ipynb
  yodogawa_feature_eng.ipynb
  yodogawa_train_model.ipynb
  yodogawa_predict_matching_score.ipynb
  yodogawa_recommendation_top5.ipynb
```

### Responsibilities
- `feature_pipeline.py`
  - reusable inference feature engineering functions
- `recommender.py`
  - load model and listings
  - compute scores
  - return Top-5 results
- `schemas.py`
  - Pydantic request/response models
- `api.py`
  - FastAPI endpoints
- `chat_agent.py`
  - LLM tool-calling integration
- `config.py`
  - project paths and environment config

---

## Required Refactoring Tasks

### 1. Save training feature metadata
During model training, persist the feature column order used by XGBoost.

Example:

```python
import json

feature_columns = X_train.columns.tolist()
with open("src/model/feature_columns.json", "w", encoding="utf-8") as f:
    json.dump(feature_columns, f, ensure_ascii=False, indent=2)
```

Also persist any of the following if applicable:
- label encoders,
- one-hot column mappings,
- station normalization rules,
- layout normalization rules,
- missing-value defaults,
- scaler or transformer objects.

### 2. Convert notebook logic into Python functions
Move reusable logic out of notebooks and into modules.

Required functions:

```python
def load_model():
    ...

def load_listings():
    ...

def engineer_inference_features(listings_df, prefs):
    ...

def score_listings(listings_df, prefs):
    ...

def recommend_top5(prefs):
    ...
```

### 3. Use cross-platform paths
Replace hard-coded Windows-style paths with `pathlib`.

Example:

```python
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "src" / "data"
MODEL_DIR = BASE_DIR / "src" / "model"
```

### 4. Add a backend API
Expose a `/recommend` endpoint with FastAPI.

### 5. Add the LLM conversation layer
The LLM should either:
- extract structured preference JSON and pass it to the backend, or
- call the recommender as a tool/function.

### 6. Keep a fallback recommender
Retain the existing rule-based recommendation notebook logic as a fallback path.

Use fallback when:
- model loading fails,
- required features are missing,
- insufficient preferences are available,
- the engineered inference pipeline is unavailable.

---

## Preference Schema
The chatbot should extract a structured preference object like this:

```json
{
  "budget_max": 95000,
  "min_area_sqm": 30,
  "max_walk_minutes": 10,
  "preferred_layouts": ["1K", "1DK", "1LDK"],
  "preferred_station": "Shin-Osaka",
  "age_max_years": 15
}
```

### Notes
- All values should be normalized before scoring.
- Missing fields are allowed, but defaults must be defined clearly.
- The service should validate this schema before running inference.

---

## FastAPI Service Spec

### Request model

```python
from pydantic import BaseModel, Field

class PreferenceRequest(BaseModel):
    budget_max: int = Field(..., ge=0)
    min_area_sqm: float = Field(..., ge=0)
    max_walk_minutes: int = Field(..., ge=0)
    preferred_layouts: list[str]
    preferred_station: str | None = None
    age_max_years: int | None = None
```

### Response shape

```json
{
  "recommendations": [
    {
      "property_name": "Sun Heights Shin-Osaka",
      "rent": 89000,
      "layout": "1LDK",
      "area_sqm": 34.2,
      "walk_minutes": 8,
      "nearest_station": "Shin-Osaka",
      "matching_score": 0.91,
      "reasons": {
        "within_budget": true,
        "layout_match": true,
        "walk_match": true,
        "station_match": true
      }
    }
  ]
}
```

### Why explanation flags matter
The LLM should **not invent ranking reasons**.

Instead, the backend should provide grounded explanation signals such as:
- `within_budget`
- `layout_match`
- `walk_match`
- `station_match`
- `area_match`
- `building_age_match`

The LLM can then convert those flags into natural language.

---

## Recommender Logic Spec

### Input
- cleaned listings dataset,
- trained model,
- structured user preferences.

### Processing
1. Load latest cleaned or engineered listing data.
2. Apply the exact same feature engineering logic used at training time.
3. Align columns to `feature_columns.json`.
4. Score each listing.
5. Sort descending by `matching_score`.
6. Return Top-5 rows.

### Output
Each recommendation should include:
- apartment identifier or property name,
- rent,
- layout,
- area,
- walk minutes,
- station,
- matching score,
- explanation flags.

---

## Critical Modeling Check
Before integrating the chatbot, confirm whether the trained model is truly **preference-aware**.

### Good case
The model was trained on features that combine:
- apartment attributes, and
- user preference compatibility features.

Examples:
- `budget_diff`
- `walk_match`
- `layout_match`
- `station_match`
- `area_gap`

In this case, the chatbot can collect user preferences and use the model meaningfully.

### Weak case
The model was trained only on apartment-side features such as:
- rent,
- size,
- layout,
- building age,
- station distance,

with no user-preference interaction features.

In that case, the chatbot can still filter and present results, but the ranking is not truly personalized. If this is the current state, retraining the model with **user-property pair features** is strongly recommended.

---

## LLM Integration Options

## Option A — Structured extraction then backend call
This is the easiest MVP.

### Flow
1. User sends natural-language request.
2. LLM extracts a validated preference JSON object.
3. Backend calls `recommend_top5(preferences)`.
4. LLM converts results into a friendly answer.

### Benefits
- simple to implement,
- easier to debug,
- lower risk of tool-calling complexity.

---

## Option B — Tool/function calling
This is the best long-term chatbot UX.

### Flow
1. User sends natural-language request.
2. LLM decides to call `recommend_yodogawa_apartments(...)`.
3. Backend runs the real recommender.
4. Tool output is returned to the LLM.
5. LLM explains the Top-5 results.

### Example function signature

```python
def recommend_yodogawa_apartments(
    budget_max: int,
    min_area_sqm: float,
    max_walk_minutes: int,
    preferred_layouts: list[str],
    preferred_station: str | None = None,
    age_max_years: int | None = None,
) -> list[dict]:
    ...
```

### Rule
The LLM must never fabricate matching scores or apartment facts not returned by the backend.

---

## Chatbot Behavior Requirements

### The chatbot should
- ask for missing essential preferences when needed,
- remember preferences across turns in session state,
- handle updates like:
  - "show cheaper ones"
  - "closer to the station"
  - "only 2LDK now"
- keep answers grounded in returned data.

### Session memory
Preference state should be stored in backend session state, not only in the LLM prompt.

Example session state:

```json
{
  "budget_max": 100000,
  "min_area_sqm": 25,
  "max_walk_minutes": 12,
  "preferred_layouts": ["1K", "1DK"],
  "preferred_station": "Juso"
}
```

---

## Example Response Style
Given backend results, the chatbot can respond like this:

> Here are the top 5 matches in Yodogawa based on your budget, preferred layout, and station access.
>
> **1. Sun Heights Shin-Osaka** — Score: 0.91  
> 89,000 JPY, 1LDK, 34.2 sqm, 8 minutes from Shin-Osaka Station.  
> This ranks highly because it is within budget, matches your preferred layout, and is close to your target station.

This explanation is acceptable only if those reasons came from backend flags.

---

## Engineering Guidelines

### Code quality requirements
- Use typed Python functions.
- Prefer `pathlib` over string paths.
- Keep notebook logic and production logic separate.
- Avoid duplicating feature engineering code in multiple places.
- Add validation and error handling around model loading and feature mismatch.

### Data requirements
- Never reorder model columns implicitly.
- Validate required columns before inference.
- Fail loudly if feature columns do not match training.

### Model persistence recommendations
Current model artifact:
- `yodogawa_match_model.pkl`

Recommended improvement:
- keep `.pkl` for immediate compatibility,
- also export an XGBoost-native model format such as `.json` or `.ubj`,
- persist feature metadata separately.

---

## Implementation Checklist

### Phase 1 — Productionize the recommender
- [ ] Extract reusable feature engineering logic from notebooks.
- [ ] Extract model loading and inference code from notebooks.
- [ ] Save `feature_columns.json`.
- [ ] Save any encoders or mappings used in training.
- [ ] Replace Windows-style paths with `pathlib`.
- [ ] Create `recommend_top5(prefs)`.

### Phase 2 — Add an API
- [ ] Create `PreferenceRequest` schema.
- [ ] Create `/recommend` FastAPI endpoint.
- [ ] Return Top-5 results in JSON.
- [ ] Return grounded explanation flags.

### Phase 3 — Add chat orchestration
- [ ] Create LLM prompt/system behavior.
- [ ] Add structured extraction or tool calling.
- [ ] Maintain user session preference state.
- [ ] Support follow-up preference updates.

### Phase 4 — Reliability
- [ ] Add rule-based fallback recommender.
- [ ] Add tests for feature alignment and scoring.
- [ ] Add logging for preferences and recommendation calls.
- [ ] Add graceful handling for missing data or invalid input.

---

## Minimum Viable Product
A successful MVP is:

> A user types a sentence with apartment preferences, and the system returns Top-5 Yodogawa apartment recommendations ranked by the trained XGBoost model.

### MVP scope
- one API endpoint,
- one chat orchestration flow,
- one model-based recommender,
- one grounded explanation layer.

---

## Acceptance Criteria
The implementation is complete when all of the following are true:

1. A user can provide apartment preferences in natural language.
2. The application converts that message into validated structured preferences.
3. The backend runs the existing trained model.
4. The system returns Top-5 recommendations sorted by matching score.
5. The chatbot explains results without hallucinating facts or scores.
6. Cross-platform path handling works.
7. The system can fall back to rule-based recommendations if the model path fails.

---

## Suggested First Milestone for Codex
Implement the following first:

1. `feature_pipeline.py`
2. `recommender.py`
3. `schemas.py`
4. `api.py`

Then verify that this works:

```bash
POST /recommend
```

with input:

```json
{
  "budget_max": 95000,
  "min_area_sqm": 30,
  "max_walk_minutes": 10,
  "preferred_layouts": ["1LDK"],
  "preferred_station": "Shin-Osaka",
  "age_max_years": 15
}
```

and output:
- a valid JSON response,
- 5 ranked listings,
- matching scores,
- explanation flags.

Once this works, add the LLM chat layer on top.

---

## Direct Build Instruction for Codex
Use the existing notebook project as the source of truth for data cleaning, feature engineering, and model behavior. Refactor notebook logic into reusable Python modules. Build a FastAPI recommendation service around the trained Yodogawa XGBoost model. Then add an LLM chat orchestration layer that extracts user preferences, calls the recommender, and explains the Top-5 results. Keep the trained model as the ranking engine, keep explanations grounded in backend outputs, and include the rule-based notebook logic as a fallback path.
