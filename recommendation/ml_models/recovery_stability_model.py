"""
Behavior Recovery & Stability Prediction Engine
Predicts how quickly users recover from setbacks and stability of health behaviors
"""
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import os
from django.conf import settings
from datetime import datetime, timedelta


class RecoveryStabilityModel:
    """ML model for predicting behavior recovery and stability"""
    
    def __init__(self):
        self.recovery_model = None
        self.stability_model = None
        self.scaler = StandardScaler()
        self.recovery_model_path = os.path.join(settings.BASE_DIR, 'recommendation', 'ml_models', 'recovery_model.pkl')
        self.stability_model_path = os.path.join(settings.BASE_DIR, 'recommendation', 'ml_models', 'stability_model.pkl')
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize or load the models"""
        if os.path.exists(self.recovery_model_path) and os.path.exists(self.stability_model_path):
            try:
                self.recovery_model = joblib.load(self.recovery_model_path)
                self.stability_model = joblib.load(self.stability_model_path)
            except:
                self._train_models()
        else:
            self._train_models()
    
    def _train_models(self):
        """Train the models with synthetic data"""
        np.random.seed(42)
        n_samples = 1000
        
        # Features: [consistency_score, adherence_rate, days_active, age, activity_level, goal_type]
        X = np.random.rand(n_samples, 6)
        X[:, 0] = np.random.uniform(0.3, 1.0, n_samples)  # consistency_score
        X[:, 1] = np.random.uniform(0.4, 1.0, n_samples)  # adherence_rate
        X[:, 2] = np.random.randint(7, 90, n_samples)  # days_active
        X[:, 3] = np.random.randint(18, 70, n_samples)  # age
        X[:, 4] = np.random.randint(0, 5, n_samples)  # activity_level
        X[:, 5] = np.random.randint(0, 4, n_samples)  # goal_type
        
        # Recovery time (days to recover from setback)
        recovery_y = 3 + (1 - X[:, 0]) * 5 + (1 - X[:, 1]) * 4 + np.random.normal(0, 1, n_samples)
        recovery_y = np.clip(recovery_y, 1, 14)
        
        # Stability score (0-1, higher is more stable)
        stability_y = X[:, 0] * 0.4 + X[:, 1] * 0.4 + (X[:, 2] / 90) * 0.2 + np.random.normal(0, 0.1, n_samples)
        stability_y = np.clip(stability_y, 0, 1)
        
        # Train recovery model
        self.recovery_model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10)
        self.recovery_model.fit(X, recovery_y)
        
        # Train stability model (classification: stable/unstable)
        stability_binary = (stability_y > 0.6).astype(int)
        self.stability_model = GradientBoostingClassifier(n_estimators=100, random_state=42, max_depth=5)
        self.stability_model.fit(X, stability_binary)
        
        # Save models
        os.makedirs(os.path.dirname(self.recovery_model_path), exist_ok=True)
        joblib.dump(self.recovery_model, self.recovery_model_path)
        joblib.dump(self.stability_model, self.stability_model_path)
    
    def calculate_metrics(self, health_data_list):
        """Calculate consistency and adherence metrics from health data"""
        if not health_data_list or len(health_data_list) < 1:
            return {
                'consistency_score': 0.5,
                'adherence_rate': 0.5,
                'days_active': len(health_data_list) if health_data_list else 0,
                'streak_days': 0,
                'missed_days': 0,
            }
        
        # Calculate consistency (how regular the data entries are)
        dates = sorted([data.date for data in health_data_list])
        intervals = []
        for i in range(1, len(dates)):
            diff = (dates[i] - dates[i-1]).days
            intervals.append(diff)
        
        if intervals:
            avg_interval = np.mean(intervals)
            consistency = 1.0 / (1.0 + avg_interval) if avg_interval > 0 else 1.0
            consistency = min(1.0, consistency * 2)  # Normalize
        else:
            consistency = 0.5
        
        # Calculate adherence (how well user follows recommendations)
        total_days = (dates[-1] - dates[0]).days + 1 if len(dates) > 1 else 1
        adherence = len(health_data_list) / max(total_days, 1)
        adherence = min(1.0, adherence)
        
        # Calculate streak
        streak = 1
        max_streak = 1
        for i in range(1, len(dates)):
            if (dates[i] - dates[i-1]).days <= 2:  # Within 2 days
                streak += 1
                max_streak = max(max_streak, streak)
            else:
                streak = 1
        
        missed_days = max(0, total_days - len(health_data_list))
        
        return {
            'consistency_score': round(consistency, 2),
            'adherence_rate': round(adherence, 2),
            'days_active': len(health_data_list),
            'streak_days': max_streak,
            'missed_days': int(missed_days),
        }
    
    def predict_recovery_time(self, consistency_score, adherence_rate, days_active, age, activity_level, goal_type):
        """Predict days to recover from a setback"""
        activity_map = {'sedentary': 0, 'light': 1, 'moderate': 2, 'active': 3, 'very_active': 4}
        goal_map = {'weight_loss': 0, 'muscle_gain': 1, 'maintenance': 2, 'general': 3}
        
        features = np.array([[
            consistency_score,
            adherence_rate,
            days_active,
            age,
            activity_map.get(activity_level, 0),
            goal_map.get(goal_type, 3)
        ]])
        
        recovery_days = self.recovery_model.predict(features)[0]
        return max(1, min(14, round(recovery_days, 1)))
    
    def predict_stability(self, consistency_score, adherence_rate, days_active, age, activity_level, goal_type):
        """Predict behavior stability (stable/unstable)"""
        activity_map = {'sedentary': 0, 'light': 1, 'moderate': 2, 'active': 3, 'very_active': 4}
        goal_map = {'weight_loss': 0, 'muscle_gain': 1, 'maintenance': 2, 'general': 3}
        
        features = np.array([[
            consistency_score,
            adherence_rate,
            days_active,
            age,
            activity_map.get(activity_level, 0),
            goal_map.get(goal_type, 3)
        ]])
        
        stability_prediction = self.stability_model.predict(features)[0]
        stability_prob = self.stability_model.predict_proba(features)[0]
        
        return {
            'is_stable': bool(stability_prediction),
            'stability_score': round(stability_prob[1] * 100, 1),  # Probability of being stable
            'risk_level': 'Low' if stability_prediction else 'High',
        }
    
    def get_recovery_recommendations(self, recovery_days, stability_score):
        """Get personalized recovery recommendations"""
        recommendations = []
        
        if recovery_days > 7:
            recommendations.append("Focus on building consistency with small, daily habits")
            recommendations.append("Set reminders to track your progress daily")
        elif recovery_days > 4:
            recommendations.append("Maintain your current routine and track progress")
            recommendations.append("Celebrate small wins to maintain motivation")
        else:
            recommendations.append("You have strong recovery patterns - keep it up!")
            recommendations.append("Consider increasing challenge level gradually")
        
        if stability_score < 50:
            recommendations.append("Build a support system or accountability partner")
            recommendations.append("Identify and remove barriers to consistency")
        elif stability_score < 70:
            recommendations.append("Focus on maintaining current habits")
            recommendations.append("Plan for potential setbacks in advance")
        else:
            recommendations.append("Your habits are well-established")
            recommendations.append("Consider adding new healthy habits")
        
        return recommendations

