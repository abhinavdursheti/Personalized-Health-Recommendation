"""
Disease Prediction Model
Predicts risk of various diseases based on health data
"""
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
import joblib
import os
from django.conf import settings


class DiseasePredictionModel:
    """ML model for disease risk prediction"""
    
    def __init__(self):
        self.models = {}
        self.model_path = os.path.join(settings.BASE_DIR, 'recommendation', 'ml_models', 'disease_models')
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize or load disease prediction models"""
        os.makedirs(self.model_path, exist_ok=True)
        
        # Diseases to predict
        self.diseases = [
            'diabetes', 'hypertension', 'obesity', 'heart_disease', 
            'osteoporosis', 'depression', 'sleep_disorder'
        ]
        
        for disease in self.diseases:
            model_file = os.path.join(self.model_path, f'{disease}_model.pkl')
            if os.path.exists(model_file):
                try:
                    self.models[disease] = joblib.load(model_file)
                except:
                    self._train_model(disease)
            else:
                self._train_model(disease)
    
    def _train_model(self, disease):
        """Train model for a specific disease"""
        np.random.seed(42)
        n_samples = 1000
        
        # Features: [age, bmi, activity_level, sleep_hours, exercise_frequency, diet_quality, family_history]
        X = np.random.rand(n_samples, 7)
        X[:, 0] = np.random.randint(18, 80, n_samples)  # age
        X[:, 1] = np.random.uniform(18, 40, n_samples)  # bmi
        X[:, 2] = np.random.randint(0, 5, n_samples)  # activity_level
        X[:, 3] = np.random.uniform(4, 10, n_samples)  # sleep_hours
        X[:, 4] = np.random.uniform(0, 1, n_samples)  # exercise_frequency
        X[:, 5] = np.random.uniform(0, 1, n_samples)  # diet_quality
        X[:, 6] = np.random.randint(0, 2, n_samples)  # family_history
        
        # Disease-specific risk calculation
        if disease == 'diabetes':
            risk = (X[:, 0] / 80) * 0.3 + ((X[:, 1] - 18) / 22) * 0.4 + (1 - X[:, 2] / 5) * 0.2 + (1 - X[:, 4]) * 0.1
        elif disease == 'hypertension':
            risk = (X[:, 0] / 80) * 0.3 + ((X[:, 1] - 18) / 22) * 0.3 + (1 - X[:, 2] / 5) * 0.2 + X[:, 6] * 0.2
        elif disease == 'obesity':
            risk = ((X[:, 1] - 18) / 22) * 0.6 + (1 - X[:, 2] / 5) * 0.3 + (1 - X[:, 5]) * 0.1
        elif disease == 'heart_disease':
            risk = (X[:, 0] / 80) * 0.3 + ((X[:, 1] - 18) / 22) * 0.3 + (1 - X[:, 2] / 5) * 0.2 + (1 - X[:, 4]) * 0.1 + X[:, 6] * 0.1
        elif disease == 'osteoporosis':
            risk = (X[:, 0] / 80) * 0.4 + (1 - X[:, 2] / 5) * 0.3 + (1 - X[:, 4]) * 0.2 + (1 - X[:, 5]) * 0.1
        elif disease == 'depression':
            risk = (1 - X[:, 3] / 10) * 0.3 + (1 - X[:, 2] / 5) * 0.3 + (1 - X[:, 4]) * 0.2 + (1 - X[:, 5]) * 0.2
        elif disease == 'sleep_disorder':
            risk = (1 - X[:, 3] / 10) * 0.5 + ((X[:, 1] - 18) / 22) * 0.3 + (1 - X[:, 2] / 5) * 0.2
        else:
            risk = np.random.uniform(0, 1, n_samples)
        
        risk = np.clip(risk, 0, 1)
        y = (risk > 0.5).astype(int)
        
        model = GradientBoostingClassifier(n_estimators=100, random_state=42, max_depth=6)
        model.fit(X, y)
        
        self.models[disease] = model
        
        # Save model
        model_file = os.path.join(self.model_path, f'{disease}_model.pkl')
        joblib.dump(model, model_file)
    
    def predict_risk(self, age, bmi, activity_level, avg_sleep_hours, exercise_frequency, diet_quality, family_history=0):
        """Predict disease risk for all diseases"""
        activity_map = {'sedentary': 0, 'light': 1, 'moderate': 2, 'active': 3, 'very_active': 4}
        
        features = np.array([[
            age,
            bmi,
            activity_map.get(activity_level, 0),
            avg_sleep_hours if avg_sleep_hours else 7,
            exercise_frequency if exercise_frequency else 0.5,
            diet_quality if diet_quality else 0.7,
            family_history
        ]])
        
        predictions = {}
        
        for disease in self.diseases:
            if disease in self.models:
                risk_prob = self.models[disease].predict_proba(features)[0]
                risk_score = risk_prob[1] * 100 if len(risk_prob) > 1 else risk_prob[0] * 100
                
                if risk_score < 30:
                    risk_level = 'low'
                elif risk_score < 60:
                    risk_level = 'medium'
                else:
                    risk_level = 'high'
                
                predictions[disease] = {
                    'risk_score': round(risk_score, 1),
                    'risk_level': risk_level,
                    'factors': self._get_factors(disease, age, bmi, activity_level, avg_sleep_hours, exercise_frequency, diet_quality),
                    'recommendations': self._get_recommendations(disease, risk_level)
                }
        
        return predictions
    
    def _get_factors(self, disease, age, bmi, activity_level, sleep, exercise, diet):
        """Get contributing factors for disease risk"""
        factors = []
        
        if disease == 'diabetes':
            if bmi > 25:
                factors.append(f"High BMI ({bmi:.1f}) increases diabetes risk")
            if age > 45:
                factors.append("Age is a risk factor for diabetes")
            if activity_level in ['sedentary', 'light']:
                factors.append("Low physical activity increases risk")
        elif disease == 'hypertension':
            if bmi > 25:
                factors.append(f"High BMI ({bmi:.1f}) increases hypertension risk")
            if age > 40:
                factors.append("Age increases hypertension risk")
            if activity_level in ['sedentary', 'light']:
                factors.append("Lack of exercise contributes to hypertension")
        elif disease == 'obesity':
            if bmi > 25:
                factors.append(f"Current BMI ({bmi:.1f}) indicates overweight/obesity")
            if activity_level in ['sedentary', 'light']:
                factors.append("Low activity level contributes to weight gain")
        elif disease == 'heart_disease':
            if bmi > 25:
                factors.append(f"High BMI ({bmi:.1f}) increases heart disease risk")
            if age > 50:
                factors.append("Age is a major risk factor")
            if activity_level in ['sedentary', 'light']:
                factors.append("Physical inactivity increases cardiovascular risk")
        elif disease == 'sleep_disorder':
            if sleep and sleep < 6:
                factors.append(f"Insufficient sleep ({sleep:.1f} hours) increases risk")
            if bmi > 25:
                factors.append(f"High BMI can affect sleep quality")
        
        if not factors:
            factors.append("Maintain healthy lifestyle to reduce risk")
        
        return factors
    
    def _get_recommendations(self, disease, risk_level):
        """Get recommendations based on disease and risk level"""
        recommendations = {
            'diabetes': {
                'low': ["Maintain healthy weight", "Regular exercise", "Balanced diet"],
                'medium': ["Lose weight if overweight", "Increase physical activity", "Monitor blood sugar", "Reduce sugar intake"],
                'high': ["Consult healthcare provider", "Weight management program", "Regular blood sugar monitoring", "Medication may be needed"]
            },
            'hypertension': {
                'low': ["Maintain healthy lifestyle", "Regular exercise", "Low sodium diet"],
                'medium': ["Reduce sodium intake", "Increase physical activity", "Monitor blood pressure", "Stress management"],
                'high': ["Consult doctor immediately", "Blood pressure medication may be needed", "Lifestyle changes essential", "Regular monitoring"]
            },
            'obesity': {
                'low': ["Maintain current weight", "Regular exercise", "Balanced diet"],
                'medium': ["Gradual weight loss", "Increase physical activity", "Calorie deficit", "Portion control"],
                'high': ["Consult nutritionist", "Structured weight loss program", "Regular exercise routine", "Medical supervision may be needed"]
            },
            'heart_disease': {
                'low': ["Maintain heart-healthy lifestyle", "Regular exercise", "Balanced diet"],
                'medium': ["Improve diet quality", "Increase cardio exercise", "Reduce stress", "Regular health checkups"],
                'high': ["Consult cardiologist", "Immediate lifestyle changes", "Medication may be required", "Regular monitoring essential"]
            },
            'sleep_disorder': {
                'low': ["Maintain sleep schedule", "Good sleep hygiene", "Regular exercise"],
                'medium': ["Improve sleep duration", "Sleep schedule consistency", "Reduce screen time before bed", "Consider sleep study"],
                'high': ["Consult sleep specialist", "Sleep study recommended", "Address underlying causes", "Medical intervention may be needed"]
            }
        }
        
        return recommendations.get(disease, {}).get(risk_level, ["Maintain healthy lifestyle", "Regular health checkups"])


