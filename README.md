# Yodogawa Matching Score Project

Notebook-based pipeline for apartment matching and Top-5 recommendation in the Yodogawa area.

## What this project does
- Cleans raw listing data from SUUMO-style exports.
- Builds engineered features for modeling.
- Trains an XGBoost-based matching model.
- Predicts matching scores and returns Top-5 properties for user preferences.
- Includes a rule-based fallback recommendation notebook.

## Project structure
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

## Environment
- Python 3.13 was used in the current notebooks.
- Main libraries:
  - pandas
  - numpy
  - scikit-learn
  - xgboost
  - jupyter

Quick setup (PowerShell):
```powershell
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
pip install pandas numpy scikit-learn xgboost jupyter
```

## Run order
Run notebooks from top to bottom in this order:

1. `yodogawa_data_cleaning.ipynb`
   - Input: `data/suumo_raw_data.csv`
   - Output: `data/yodogawa_data_cleaning.csv`
2. `yodogawa_feature_eng.ipynb`
   - Input: `data/yodogawa_data_cleaning.csv`
   - Output: `data/yodogawa_feature_eng.csv`
3. `yodogawa_train_model.ipynb`
   - Input: `data/yodogawa_feature_eng.csv`
   - Output: `model/yodogawa_match_model.pkl`
4. `yodogawa_predict_matching_score.ipynb`
   - Uses engineered data + trained model to produce Top-5 recommendations.

Optional:
- `yodogawa_recommendation_top5.ipynb` for rule-based recommendation flow.

## Notes
- Paths in notebooks currently use Windows-style relative paths (for example `./data/...`).
- If you run on macOS/Linux, adjust path separators as needed.
- Large or sensitive CSV/model files are excluded by default in `.gitignore`.
