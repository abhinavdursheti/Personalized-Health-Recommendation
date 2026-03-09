"""
predict_models.py
=================
Prediction helpers for the Personalized Health Recommendation System.

Loads the pre‑trained .pkl models from ml_models/ and exposes three
public functions that can be imported by Django views (or any caller):

  • predict_lifestyle_risk(bmi, age, sleep_hours, activity_level, stress_level, daily_steps)
  • predict_recovery_score(sleep_hours, activity_level, calories_consumed, stress_level)
  • predict_exercise_category(bmi, age, sleep_hours, activity_level, stress_level, daily_steps)
"""

import os
import numpy as np
import pandas as pd
import joblib


# ---------------------------------------------------------------------------
# Paths — resolve once at import time
# ---------------------------------------------------------------------------
MODEL_DIR = os.path.dirname(os.path.abspath(__file__))

_linear_regression = None
_decision_tree = None
_random_forest = None
_label_encoder = None


def _load_models():
    """Lazy‑load models on first call so import stays lightweight."""
    global _linear_regression, _decision_tree, _random_forest, _label_encoder

    if _random_forest is not None:
        return  # already loaded

    _linear_regression = joblib.load(os.path.join(MODEL_DIR, "linear_regression.pkl"))
    _decision_tree = joblib.load(os.path.join(MODEL_DIR, "decision_tree.pkl"))
    _random_forest = joblib.load(os.path.join(MODEL_DIR, "random_forest.pkl"))

    encoder_path = os.path.join(MODEL_DIR, "bmi_label_encoder.pkl")
    if os.path.exists(encoder_path):
        _label_encoder = joblib.load(encoder_path)


def _build_features_clf(bmi, age, sleep_hours, activity_level, stress_level, daily_steps):
    """Return a DataFrame with proper column names for Classifiers (.predict())."""
    return pd.DataFrame(
        [[bmi, age, sleep_hours, activity_level, stress_level, daily_steps]],
        columns=["BMI", "Age", "Sleep Duration", "Physical Activity Level",
                 "Stress Level", "Daily Steps"]
    )

def _build_features_lr(sleep_hours, activity_level, calories_consumed, stress_level):
    """Return a DataFrame with proper column names for Linear Regression."""
    return pd.DataFrame(
        [[sleep_hours, activity_level, calories_consumed, stress_level]],
        columns=["Sleep Duration", "Physical Activity Level", "Calories Consumed", "Stress Level"]
    )


def _decode_bmi(encoded_value):
    """Convert numeric label back to human‑readable BMI category string."""
    if _label_encoder is not None:
        return _label_encoder.inverse_transform([int(encoded_value)])[0]
    mapping = {0: "Normal", 1: "Obese", 2: "Overweight"}
    return mapping.get(int(encoded_value), "Unknown")


# -----------------------------------------------------------------------
# Public prediction functions
# -----------------------------------------------------------------------

def predict_lifestyle_risk(bmi, age, sleep_hours, activity_level,
                           stress_level, daily_steps):
    """
    Predict the lifestyle‑risk level using the Random Forest model.

    Returns
    -------
    dict
        {
            "risk_label": str,          # e.g. "Normal", "Overweight", "Obese"
            "risk_code": int,           # encoded numeric label
            "confidence": float,        # max probability (0‑1)
            "probabilities": dict       # class → probability
        }
    """
    _load_models()
    features = _build_features_clf(bmi, age, sleep_hours, activity_level,
                                   stress_level, daily_steps)

    prediction = _random_forest.predict(features)[0]
    probas = _random_forest.predict_proba(features)[0]

    # Build probability dict with human labels
    prob_dict = {}
    for idx, p in enumerate(probas):
        label = _decode_bmi(idx) if _label_encoder else str(idx)
        prob_dict[label] = round(float(p), 4)

    if bmi >= 30:
        actual_label = "Obese"
    elif bmi >= 25:
        actual_label = "Overweight"
    elif bmi >= 18.5:
        actual_label = "Normal"
    else:
        actual_label = "Underweight"

    return {
        "risk_label": actual_label,
        "risk_code": int(prediction),
        "confidence": round(float(max(probas)), 4),
        "probabilities": prob_dict,
        "ml_predicted_label": _decode_bmi(prediction),
    }


def predict_recovery_score(sleep_hours, activity_level,
                           calories_consumed, stress_level, previous_score=None):
    """
    Estimate a recovery score (0‑100) using the Linear Regression model.
    """
    _load_models()
    features = _build_features_lr(sleep_hours, activity_level,
                                  calories_consumed, stress_level)

    prediction = float(_linear_regression.predict(features)[0])

    # Bound output 0-100 directly from regression
    recovery = max(0.0, min(100.0, prediction))

    # Apply stabilization layer if previous score exists
    if previous_score is not None:
        if abs(recovery - previous_score) > 25:
            sign = 1 if recovery > previous_score else -1
            recovery = previous_score + sign * 25
        # Ensure it stays within bounds after stabilization
        recovery = max(0.0, min(100.0, recovery))

    if recovery >= 80:
        status = "Excellent"
    elif recovery >= 60:
        status = "Good"
    elif recovery >= 40:
        status = "Fair"
    else:
        status = "Poor"

    return {
        "recovery_score": round(recovery, 2),
        "raw_prediction": round(prediction, 4),
        "status": status,
    }


def predict_exercise_category(bmi, age, sleep_hours, activity_level,
                              stress_level, daily_steps):
    """
    Classify the user's exercise / lifestyle category using the
    Decision Tree model.

    Returns
    -------
    dict
        {
            "category_label": str,      # e.g. "Normal", "Overweight", "Obese"
            "category_code": int,       # encoded numeric label
            "recommendation": str       # brief lifestyle suggestion
        }
    """
    _load_models()
    features = _build_features_clf(bmi, age, sleep_hours, activity_level,
                                   stress_level, daily_steps)

    prediction = _decision_tree.predict(features)[0]
    label = _decode_bmi(prediction)

    # Provide a contextual recommendation based on the predicted category
    recommendations = {
        "Normal": (
            "Your lifestyle metrics look healthy. Continue your current "
            "exercise routine and maintain balanced sleep habits."
        ),
        "Overweight": (
            "Consider increasing daily physical activity to at least 45 min "
            "and aim for 7‑8 hours of quality sleep to improve your health profile."
        ),
        "Obese": (
            "A structured exercise programme and dietary adjustments are "
            "recommended.  Consult a healthcare professional for a "
            "personalised plan."
        ),
    }

    return {
        "category_label": label,
        "category_code": int(prediction),
        "recommendation": recommendations.get(label, "Maintain a balanced lifestyle."),
    }


# -----------------------------------------------------------------------
# Quick CLI test
# -----------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 60)
    print("  Quick prediction test")
    print("=" * 60)

    test_input_clf = {
        "bmi": 26.0,
        "age": 35,
        "sleep_hours": 7.0,
        "activity_level": 60,
        "stress_level": 5,
        "daily_steps": 7000,
    }
    
    test_input_lr = {
        "sleep_hours": 7.0,
        "activity_level": 60,
        "calories_consumed": 2200,
        "stress_level": 5,
    }
    print(f"\n  Clf Input: {test_input_clf}")
    print(f"  LR Input : {test_input_lr}\n")

    risk   = predict_lifestyle_risk(**test_input_clf)
    score  = predict_recovery_score(**test_input_lr)
    cat    = predict_exercise_category(**test_input_clf)

    print(f"  Lifestyle Risk     : {risk}")
    print(f"  Recovery Score     : {score}")
    print(f"  Exercise Category  : {cat}")
    print("=" * 60)
