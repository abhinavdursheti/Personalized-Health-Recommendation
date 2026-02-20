"""
What-If Health Simulator ML Model
Predicts future health outcomes based on hypothetical scenarios
"""
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
import joblib
import os
from django.conf import settings
from datetime import datetime, timedelta


class HealthSimulatorModel:
    """ML model for health outcome simulation"""
    
    def __init__(self):
        self.weight_model = None
        self.stability_model = None
        self.recovery_model = None
        self.model_path = os.path.join(settings.BASE_DIR, 'recommendation', 'ml_models', 'simulator_model.pkl')
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize or train the models"""
        if os.path.exists(self.model_path):
            try:
                models = joblib.load(self.model_path)
                self.weight_model = models.get('weight')
                self.stability_model = models.get('stability')
                self.recovery_model = models.get('recovery')
            except:
                self._train_models()
        else:
            self._train_models()
    
    def _train_models(self):
        """Train models with synthetic data"""
        np.random.seed(42)
        n_samples = 1000
        
        # Features: [current_weight, sleep_hours, exercise_minutes, days, age, bmi, activity_level]
        X = np.random.rand(n_samples, 7)
        X[:, 0] = np.random.uniform(50, 120, n_samples)  # current_weight
        X[:, 1] = np.random.uniform(5, 10, n_samples)  # sleep_hours
        X[:, 2] = np.random.uniform(0, 90, n_samples)  # exercise_minutes
        X[:, 3] = np.random.uniform(7, 30, n_samples)  # days
        X[:, 4] = np.random.uniform(18, 65, n_samples)  # age
        X[:, 5] = np.random.uniform(18, 35, n_samples)  # bmi
        X[:, 6] = np.random.uniform(0, 4, n_samples)  # activity_level (0-4)
        
        # Weight change prediction (negative = loss, positive = gain)
        # More exercise and better sleep = weight loss
        y_weight = -0.1 * X[:, 2] + 0.05 * (X[:, 1] - 7) ** 2 - 0.02 * X[:, 3] + np.random.normal(0, 0.5, n_samples)
        
        # Stability score (0-100)
        # Better sleep and consistent exercise = higher stability
        y_stability = 50 + 5 * X[:, 1] + 0.3 * X[:, 2] - 0.1 * abs(X[:, 1] - 7.5) + np.random.normal(0, 5, n_samples)
        y_stability = np.clip(y_stability, 0, 100)
        
        # Recovery speed (days to recover from setback)
        # Better habits = faster recovery
        y_recovery = 10 - 0.5 * X[:, 1] - 0.05 * X[:, 2] + 0.1 * X[:, 3] + np.random.normal(0, 1, n_samples)
        y_recovery = np.clip(y_recovery, 1, 30)
        
        # Train models
        self.weight_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.weight_model.fit(X, y_weight)
        
        self.stability_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.stability_model.fit(X, y_stability)
        
        self.recovery_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.recovery_model.fit(X, y_recovery)
        
        # Save models
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump({
            'weight': self.weight_model,
            'stability': self.stability_model,
            'recovery': self.recovery_model
        }, self.model_path)
    
    def simulate_scenario(self, current_weight, current_sleep, current_exercise, 
                         new_sleep, new_exercise, days, age, bmi, activity_level):
        """
        Simulate health outcomes for a what-if scenario
        
        Args:
            current_weight: Current weight in kg
            current_sleep: Current average sleep hours
            current_exercise: Current average exercise minutes
            new_sleep: Hypothetical sleep hours
            new_exercise: Hypothetical exercise minutes
            days: Number of days to simulate
            age: User age
            bmi: Current BMI
            activity_level: Activity level (0-4: sedentary, light, moderate, active, very_active)
        
        Returns:
            dict with predicted outcomes
        """
        activity_map = {
            'sedentary': 0,
            'light': 1,
            'moderate': 2,
            'active': 3,
            'very_active': 4
        }
        activity_encoded = activity_map.get(activity_level, 0)
        
        # Prepare features
        features = np.array([[
            current_weight,
            new_sleep,
            new_exercise,
            days,
            age,
            bmi,
            activity_encoded
        ]])
        
        # Predict outcomes
        weight_change = self.weight_model.predict(features)[0]
        predicted_weight = current_weight + weight_change
        
        stability_score = self.stability_model.predict(features)[0]
        stability_score = max(0, min(100, stability_score))
        
        recovery_days = self.recovery_model.predict(features)[0]
        recovery_days = max(1, min(30, recovery_days))
        
        # Calculate improvement metrics
        sleep_improvement = new_sleep - current_sleep
        exercise_improvement = new_exercise - current_exercise
        
        # Determine stability level
        if stability_score >= 80:
            stability_level = 'excellent'
        elif stability_score >= 60:
            stability_level = 'good'
        elif stability_score >= 40:
            stability_level = 'moderate'
        else:
            stability_level = 'needs_improvement'
        
        # Determine recovery speed
        if recovery_days <= 5:
            recovery_speed = 'very_fast'
        elif recovery_days <= 10:
            recovery_speed = 'fast'
        elif recovery_days <= 15:
            recovery_speed = 'moderate'
        else:
            recovery_speed = 'slow'
        
        return {
            'predicted_weight': round(predicted_weight, 2),
            'weight_change': round(weight_change, 2),
            'stability_score': round(stability_score, 1),
            'stability_level': stability_level,
            'recovery_days': round(recovery_days, 1),
            'recovery_speed': recovery_speed,
            'sleep_improvement': round(sleep_improvement, 1),
            'exercise_improvement': round(exercise_improvement, 1),
            'days_simulated': days,
        }


