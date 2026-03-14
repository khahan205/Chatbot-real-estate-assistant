# Yodogawa-real-estate
# 🏠 Apartment Rent Prediction using Machine Learning
An end-to-end data science project analyzing Japanese housing data to understand price patterns and identify potentially underpriced properties.
## 📌 Project Overview

This project builds a machine learning pipeline to predict apartment rental prices based on property characteristics such as area, distance to the nearest station, and building age.

The goal is to analyze housing data, understand the key factors affecting rental prices, and build predictive models that estimate the expected rent of a property. The project also explores the possibility of identifying **underpriced apartments** by comparing actual rent with model predictions.

---

## 📊 Dataset

The dataset contains apartment listings with features describing the property and its location.

### Main Features

| Feature                     | Description                               |
| --------------------------- | ----------------------------------------- |
| area_m2                     | Apartment size (square meters)            |
| walking_distance_to_station | Walking time to nearest station (minutes) |
| building_age                | Age of the building (years)               |
| floor_ratio                 | Floor level indicator                     |
| price_per_m2                | Rent per square meter                     |
| rent                        | Target variable (monthly rent)            |

The dataset includes Japanese real estate attributes and was cleaned and engineered for machine learning analysis.

---

## ⚙️ Project Pipeline

The project follows a typical **machine learning workflow**:

### 1️⃣ Data Cleaning

* Remove invalid values
* Handle missing data
* Filter outliers

### 2️⃣ Feature Engineering

* Create new features such as:

  * `price_per_m2`
  * `distance_bin`
  * `age_bin`

### 3️⃣ Exploratory Data Analysis (EDA)

Visualizations used to understand market patterns:

* Rent vs Distance to Station
* Rent vs Building Age
* Price per m² vs Area

### 4️⃣ Model Training

Several models were trained and compared:

* Linear Regression
* Random Forest
* XGBoost
* Tuned XGBoost (GridSearch)

### 5️⃣ Model Evaluation

Models were evaluated using:

* **MAE (Mean Absolute Error)**
* **RMSE (Root Mean Squared Error)**

### 6️⃣ Cross Validation

K-Fold Cross Validation was used to evaluate model stability.

### 7️⃣ Model Explainability

Model predictions were interpreted using SHAP to understand which features influence rent the most.

### 8️⃣ Market Insight

The model was used to detect **potentially underpriced apartments** by comparing predicted rent with actual rent.

---

## 📈 Model Performance

| Model             | MAE | RMSE |
| ----------------- | --- | ---- |
| Linear Regression | -   | -    |
| Random Forest     | -   | -    |
| XGBoost           | -   | -    |
| Tuned XGBoost     | -   | -    |



---

## 📊 Key Insights

Some important insights from the analysis:

* Apartments closer to train stations tend to have higher rents.
* Newer buildings command higher rental prices.
* Smaller apartments often have higher price per square meter.
* Distance to station and apartment size are among the most influential features.

---

## 🧠 Technologies Used

* Python
* Pandas
* NumPy
* Matplotlib
* Scikit-learn
* XGBoost
* SHAP

---

## 📂 Repository Structure

```
housing-ml-project
│
├── data
│   └── dataset.csv
│
├── notebook
│   └── housing_analysis.ipynb
│
├── src
│   └── preprocessing.py
│
└── README.md
```

---

## 🚀 Future Improvements

Possible improvements for this project:

* Add more location-based features
* Use geospatial analysis
* Deploy the model as an API
* Build an interactive dashboard

---

## 📬 Author

This project was created as a learning project in **Machine Learning and Data Analysis**.
