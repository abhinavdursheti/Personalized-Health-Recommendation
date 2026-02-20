"""
Sleep Recommendation Model
Uses rule-based and predictive models for sleep recommendations
"""
import numpy as np
from sklearn.linear_model import LinearRegression
import joblib
import os
from django.conf import settings


class SleepRecommendationModel:
    """ML model for sleep recommendations"""
    
    def __init__(self):
        self.model = None
        self.model_path = os.path.join(settings.BASE_DIR, 'recommendation', 'ml_models', 'sleep_model.pkl')
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize or load the model"""
        if os.path.exists(self.model_path):
            try:
                self.model = joblib.load(self.model_path)
            except:
                self._train_model()
        else:
            self._train_model()
    
    def _train_model(self):
        """Train the model with synthetic data"""
        np.random.seed(42)
        n_samples = 500
        
        # Features: [age, activity_level, bmi, exercise_minutes]
        X = np.random.rand(n_samples, 4)
        X[:, 0] = np.random.randint(18, 70, n_samples)  # age
        X[:, 1] = np.random.randint(0, 5, n_samples)  # activity level
        X[:, 2] = np.random.uniform(18, 35, n_samples)  # BMI
        X[:, 3] = np.random.randint(0, 120, n_samples)  # exercise minutes
        
        # Target: optimal sleep hours
        y = 8 - (X[:, 0] / 100) + (X[:, 1] * 0.2) + (X[:, 3] / 60) + np.random.normal(0, 0.5, n_samples)
        y = np.clip(y, 6, 10)  # Clamp between 6-10 hours
        
        self.model = LinearRegression()
        self.model.fit(X, y)
        
        # Save model
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump(self.model, self.model_path)
    
    def predict_sleep_hours(self, age, activity_level, bmi, exercise_minutes=0):
        """Predict optimal sleep duration"""
        activity_map = {'sedentary': 0, 'light': 1, 'moderate': 2, 'active': 3, 'very_active': 4}
        
        features = np.array([[
            age,
            activity_map.get(activity_level, 0),
            bmi,
            exercise_minutes
        ]])
        
        predicted_hours = self.model.predict(features)[0]
        
        # Age-based adjustments
        if age < 18:
            predicted_hours = max(8, min(10, predicted_hours + 1))
        elif age >= 65:
            predicted_hours = max(7, min(9, predicted_hours - 0.5))
        
        return round(max(6, min(10, predicted_hours)), 1)
    
    def get_sleep_schedule(self, sleep_hours, wake_time_preference='07:00'):
        """Calculate optimal bedtime based on wake time"""
        try:
            wake_hour, wake_min = map(int, wake_time_preference.split(':'))
        except:
            wake_hour, wake_min = 7, 0
        
        # Calculate bedtime (accounting for 15-20 min to fall asleep)
        bedtime_hour = wake_hour - int(sleep_hours) - 1
        bedtime_min = 60 - wake_min - 15  # 15 min buffer
        
        if bedtime_min < 0:
            bedtime_hour -= 1
            bedtime_min += 60
        
        if bedtime_hour < 0:
            bedtime_hour += 24
        
        bedtime = f"{bedtime_hour:02d}:{bedtime_min:02d}"
        
        return {
            'bedtime': bedtime,
            'wake_time': wake_time_preference,
            'sleep_duration': sleep_hours,
            'sleep_cycles': round(sleep_hours / 1.5, 1),  # ~1.5 hours per cycle
        }
    
    def get_sleep_tips(self, age, activity_level):
        """Get personalized sleep hygiene tips"""
        tips = [
            "Maintain a consistent sleep schedule, even on weekends",
            "Create a relaxing bedtime routine (reading, meditation, warm bath)",
            "Keep your bedroom cool, dark, and quiet",
            "Avoid screens (phone, TV, computer) 1 hour before bedtime",
            "Limit caffeine intake, especially after 2 PM",
            "Avoid large meals and alcohol close to bedtime",
            "Get regular exercise, but not too close to bedtime",
        ]
        
        if activity_level in ['active', 'very_active']:
            tips.append("Consider a post-workout recovery routine to help you wind down")
        
        if age >= 65:
            tips.append("Take short naps (20-30 min) if needed, but avoid long naps")
        
        return tips







