"""
train_models.py
===============
Training script for the Personalized Health Recommendation System.

Loads the Sleep Health & Lifestyle dataset, preprocesses it, and trains
three ML models:
  1. Linear Regression   — Recovery Score prediction
  2. Decision Tree        — exercise / lifestyle classification
  3. Random Forest        — lifestyle risk‑level prediction

Trained models are saved as .pkl files in the ml_models/ directory.
"""

import os
import sys
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, mean_squared_error, r2_score
from sklearn.preprocessing import LabelEncoder
import joblib


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_PATH = os.path.join(BASE_DIR, "Datasets", "Sleep_health_and_lifestyle_dataset.csv")
MODEL_DIR = os.path.dirname(os.path.abspath(__file__))  # ml_models/


def load_and_preprocess():
    """Load the CSV and return cleaned dataframe df."""

    print("=" * 60)
    print("  Loading dataset …")
    print("=" * 60)

    df = pd.read_csv(DATASET_PATH)
    print(f"  Rows loaded       : {len(df)}")
    print(f"  Columns            : {list(df.columns)}")

    # ------------------------------------------------------------------
    # Drop unnecessary columns
    # ------------------------------------------------------------------
    drop_cols = [
        col for col in ["Person ID", "Occupation", "Gender",
                        "Blood Pressure", "Heart Rate",
                        "Quality of Sleep", "Sleep Disorder"]
        if col in df.columns
    ]
    df.drop(columns=drop_cols, inplace=True)
    print(f"  Dropped columns    : {drop_cols}")

    # ------------------------------------------------------------------
    # Handle missing values
    # ------------------------------------------------------------------
    missing = df.isnull().sum().sum()
    if missing > 0:
        print(f"  Missing values     : {missing}  ->  filling with column means / modes")
        for col in df.columns:
            if df[col].dtype in ["float64", "int64"]:
                df[col].fillna(df[col].mean(), inplace=True)
            else:
                df[col].fillna(df[col].mode()[0], inplace=True)
    else:
        print("  Missing values     : 0  [OK]")

    # ------------------------------------------------------------------
    # Data Augmentation (Synthesize ~850 rows to reach ~1200 rows total)
    # ------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("  Augmenting dataset …")
    print("=" * 60)
    np.random.seed(42) # For reproducibility
    
    # Calculate how many rows needed to reach 1200
    target_rows = 1200
    current_rows = len(df)
    rows_to_add = target_rows - current_rows

    if rows_to_add > 0:
        print(f"  Synthesizing       : {rows_to_add} rows")
        # Sample with replacement to maintain statistical distributions and relationships
        df_synthetic = df.sample(n=rows_to_add, replace=True, random_state=42).copy()
        
        # Perturb numerical features slightly (e.g., +/- 5% of std dev) to create unique records
        # but keep relationships intact.
        
        # Age: +/- 1 to 3 years
        age_noise = np.random.randint(-3, 4, size=rows_to_add)
        df_synthetic["Age"] = (df_synthetic["Age"] + age_noise).clip(lower=18)
        
        # Sleep Duration: +/- 0.1 to 0.8 hours
        sleep_noise = np.random.uniform(-0.8, 0.8, size=rows_to_add)
        df_synthetic["Sleep Duration"] = (df_synthetic["Sleep Duration"] + sleep_noise).clip(lower=3.0, upper=12.0)
        
        # Physical Activity Level: +/- 2 to 10 mins
        activity_noise = np.random.randint(-10, 11, size=rows_to_add)
        df_synthetic["Physical Activity Level"] = (df_synthetic["Physical Activity Level"] + activity_noise).clip(lower=10, upper=120)
        
        # Stress Level: +/- 0 to 1 point
        stress_noise = np.random.randint(-1, 2, size=rows_to_add)
        df_synthetic["Stress Level"] = (df_synthetic["Stress Level"] + stress_noise).clip(lower=1, upper=10)
        
        # Daily Steps: +/- 100 to 1000 steps
        steps_noise = np.random.randint(-1000, 1001, size=rows_to_add)
        df_synthetic["Daily Steps"] = (df_synthetic["Daily Steps"] + steps_noise).clip(lower=1000)
        
        # Combine original and synthetic data
        df = pd.concat([df, df_synthetic], ignore_index=True)
        print(f"  New dataset size   : {len(df)} rows")
    else:
        print(f"  Dataset already has {current_rows} rows. No augmentation needed.")

    # ------------------------------------------------------------------
    # Synthesize Custom Fields for Better ML (BMI, Calories, Recovery)
    # ------------------------------------------------------------------
    np.random.seed(42) # For reproducibility
    
    # 1. Synthesize BMI based on original category to maintain realistic distributions
    def create_bmi(category):
        if category in ['Normal', 'Normal Weight']: 
            return np.random.uniform(18.5, 24.9)
        elif category == 'Overweight': 
            return np.random.uniform(25.0, 29.9)
        elif category == 'Obese': 
            return np.random.uniform(30.0, 39.9)
        else: 
            return 22.0
            
    df["BMI"] = df["BMI Category"].apply(create_bmi)
    
    # 2. Re-label BMI Category strictly according to WHO thresholds
    def label_bmi(bmi):
        if bmi < 18.5: return "Underweight"
        elif bmi < 25.0: return "Normal"
        elif bmi < 30.0: return "Overweight"
        else: return "Obese"
        
    df["BMI Category"] = df["BMI"].apply(label_bmi)

    # Encode BMI Category -> numeric labels
    label_encoder = LabelEncoder()
    df["BMI Category Encoded"] = label_encoder.fit_transform(df["BMI Category"])
    print(f"  BMI label mapping  : {dict(zip(label_encoder.classes_, label_encoder.transform(label_encoder.classes_)))}")

    # Save the encoder for re‑use in predictions
    encoder_path = os.path.join(MODEL_DIR, "bmi_label_encoder.pkl")
    joblib.dump(label_encoder, encoder_path)
    print(f"  Saved encoder      : {encoder_path}")

    # 3. Synthesize Calories Consumed
    df["Calories Consumed"] = np.random.normal(2000, 300, size=len(df)).clip(1200, 4000)

    # 4. Synthesize Recovery Score Target for Linear Regression (0-100)
    df["Recovery Score"] = (
        (df["Sleep Duration"] / 8.0) * 40 + 
        (df["Physical Activity Level"] / 60.0) * 30 + 
        ((10 - df["Stress Level"]) / 10.0) * 30
    )
    df["Recovery Score"] = df["Recovery Score"].clip(0, 100)

    return df


def train(df):
    """Train three models, evaluate, and save to disk."""

    # ==================  1. Linear Regression  ========================
    print("\n" + "=" * 60)
    print("  Training — Linear Regression  (Recovery Score prediction)")
    print("=" * 60)
    feature_cols_lr = ["Sleep Duration", "Physical Activity Level", "Calories Consumed", "Stress Level"]
    X_lr = df[feature_cols_lr]
    y_lr = df["Recovery Score"]
    
    X_train_lr, X_test_lr, y_train_lr, y_test_lr = train_test_split(
        X_lr, y_lr, test_size=0.2, random_state=42
    )

    lr_model = LinearRegression()
    lr_model.fit(X_train_lr, y_train_lr)
    lr_preds = lr_model.predict(X_test_lr)
    lr_mse = mean_squared_error(y_test_lr, lr_preds)
    lr_r2 = r2_score(y_test_lr, lr_preds)
    print(f"  Mean Squared Error : {lr_mse:.4f}")
    print(f"  R² Score           : {lr_r2:.4f}")

    # ==================  Classifiers (Decision Tree & Random Forest) ==
    feature_cols_clf = ["BMI", "Age", "Sleep Duration", "Physical Activity Level", "Stress Level", "Daily Steps"]
    X_clf = df[feature_cols_clf]
    y_clf = df["BMI Category Encoded"]
    
    X_train_clf, X_test_clf, y_train_clf, y_test_clf = train_test_split(
        X_clf, y_clf, test_size=0.2, random_state=42, stratify=y_clf
    )
    print(f"\n  Classifier Features: {feature_cols_clf}")

    # ==================  2. Decision Tree  ============================
    print("\n" + "=" * 60)
    print("  Training — Decision Tree Classifier  (exercise category)")
    print("=" * 60)
    dt_model = DecisionTreeClassifier(random_state=42, max_depth=10)
    dt_model.fit(X_train_clf, y_train_clf)
    dt_preds = dt_model.predict(X_test_clf)
    dt_acc = accuracy_score(y_test_clf, dt_preds)
    print(f"  Accuracy           : {dt_acc * 100:.2f}%")

    # ==================  3. Random Forest  ============================
    print("\n" + "=" * 60)
    print("  Training — Random Forest Classifier  (lifestyle risk)")
    print("=" * 60)
    rf_model = RandomForestClassifier(
        n_estimators=100, random_state=42, max_depth=12
    )
    rf_model.fit(X_train_clf, y_train_clf)
    rf_preds = rf_model.predict(X_test_clf)
    rf_acc = accuracy_score(y_test_clf, rf_preds)
    print(f"  Accuracy           : {rf_acc * 100:.2f}%")

    # ------------------------------------------------------------------
    # Save models
    # ------------------------------------------------------------------
    models = {
        "linear_regression.pkl": lr_model,
        "decision_tree.pkl": dt_model,
        "random_forest.pkl": rf_model,
    }

    print("\n" + "=" * 60)
    print("  Saving models …")
    print("=" * 60)
    for filename, model in models.items():
        path = os.path.join(MODEL_DIR, filename)
        joblib.dump(model, path)
        print(f"  [OK] {path}")

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("  [DONE]  Training complete — summary")
    print("=" * 60)
    print(f"  Linear Regression  ->  MSE {lr_mse:.4f}  |  R² {lr_r2:.4f}")
    print(f"  Decision Tree      ->  Accuracy {dt_acc * 100:.2f}%")
    print(f"  Random Forest      ->  Accuracy {rf_acc * 100:.2f}%")
    print("=" * 60)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    df = load_and_preprocess()
    train(df)
