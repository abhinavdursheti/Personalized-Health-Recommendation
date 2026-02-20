"""
Behavior-Cause Correlation Engine
Identifies correlations between behaviors and health outcomes (Root-Cause Analysis)
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from scipy import stats
import joblib
import os
from django.conf import settings


class CorrelationModel:
    """ML model for identifying behavior-cause correlations"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.model_path = os.path.join(settings.BASE_DIR, 'recommendation', 'ml_models', 'correlation_model.pkl')
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
        
        # Features: [sleep_hours, exercise_minutes, calories, consistency]
        X = np.random.rand(n_samples, 4)
        X[:, 0] = np.random.uniform(5, 9, n_samples)  # sleep_hours
        X[:, 1] = np.random.uniform(0, 120, n_samples)  # exercise_minutes
        X[:, 2] = np.random.uniform(1200, 3000, n_samples)  # calories
        X[:, 3] = np.random.uniform(0.3, 1.0, n_samples)  # consistency
        
        # Target: weight change (negative = loss, positive = gain)
        y = -0.1 * (X[:, 0] - 7) - 0.01 * X[:, 1] + 0.0003 * (X[:, 2] - 2000) - 0.5 * (1 - X[:, 3]) + np.random.normal(0, 0.2, n_samples)
        
        self.model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10)
        self.model.fit(X, y)
        
        # Save model
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump(self.model, self.model_path)
    
    def analyze_correlations(self, health_data_list):
        """Analyze correlations between behaviors and outcomes"""
        if not health_data_list or len(health_data_list) < 1:
            return {
                'insights': [],
                'correlations': {},
                'root_causes': ['Continue tracking to identify patterns. More data will provide better insights.'],
                'data_points': 0,
                'message': 'Add more data points for detailed correlation analysis'
            }
        
        # Prepare data
        data = []
        for entry in health_data_list:
            data.append({
                'date': entry.date,
                'weight': entry.weight,
                'sleep_hours': entry.sleep_hours if entry.sleep_hours else None,
                'exercise_minutes': entry.exercise_minutes if entry.exercise_minutes else None,
                'calories_consumed': entry.calories_consumed if entry.calories_consumed else None,
            })
        
        df = pd.DataFrame(data)
        df = df.sort_values('date')
        
        # Calculate weight change
        df['weight_change'] = df['weight'].diff()
        df['weight_trend'] = df['weight'].rolling(window=7, min_periods=1).mean()
        
        insights = []
        correlations = {}
        root_causes = []
        
        # Analyze sleep correlation
        if df['sleep_hours'].notna().sum() >= 2:
            sleep_data = df[df['sleep_hours'].notna()]
            if len(sleep_data) > 1:
                corr_sleep = sleep_data['sleep_hours'].corr(sleep_data['weight_change'])
                if not np.isnan(corr_sleep):
                    correlations['sleep'] = round(corr_sleep, 3)
                    if abs(corr_sleep) > 0.3:
                        if corr_sleep < -0.3:
                            insights.append({
                                'behavior': 'Sleep Hours',
                                'impact': 'Positive',
                                'correlation': round(corr_sleep, 2),
                                'insight': f'When you sleep more, your weight tends to decrease. Optimal: 7-9 hours.',
                                'recommendation': 'Maintain consistent sleep schedule of 7-9 hours'
                            })
                            root_causes.append('Insufficient sleep may be contributing to weight management challenges')
                        else:
                            insights.append({
                                'behavior': 'Sleep Hours',
                                'impact': 'Negative',
                                'correlation': round(corr_sleep, 2),
                                'insight': f'Excessive sleep may be affecting your weight. Target: 7-9 hours.',
                                'recommendation': 'Maintain optimal sleep duration of 7-9 hours'
                            })
        
        # Analyze exercise correlation
        if df['exercise_minutes'].notna().sum() >= 2:
            exercise_data = df[df['exercise_minutes'].notna()]
            if len(exercise_data) > 1:
                corr_exercise = exercise_data['exercise_minutes'].corr(exercise_data['weight_change'])
                if not np.isnan(corr_exercise):
                    correlations['exercise'] = round(corr_exercise, 3)
                    if abs(corr_exercise) > 0.3:
                        if corr_exercise < -0.3:
                            insights.append({
                                'behavior': 'Exercise Minutes',
                                'impact': 'Positive',
                                'correlation': round(corr_exercise, 2),
                                'insight': f'More exercise correlates with weight loss. Current avg: {exercise_data["exercise_minutes"].mean():.0f} min/day.',
                                'recommendation': 'Increase exercise frequency to 30-60 minutes daily'
                            })
                            root_causes.append('Regular exercise is a key factor in your weight management')
        
        # Analyze calories correlation
        if df['calories_consumed'].notna().sum() >= 2:
            calories_data = df[df['calories_consumed'].notna()]
            if len(calories_data) > 1:
                corr_calories = calories_data['calories_consumed'].corr(calories_data['weight_change'])
                if not np.isnan(corr_calories):
                    correlations['calories'] = round(corr_calories, 3)
                    if abs(corr_calories) > 0.3:
                        if corr_calories > 0.3:
                            avg_cal = calories_data['calories_consumed'].mean()
                            insights.append({
                                'behavior': 'Calories Consumed',
                                'impact': 'Negative',
                                'correlation': round(corr_calories, 2),
                                'insight': f'Higher calorie intake correlates with weight gain. Current avg: {avg_cal:.0f} cal/day.',
                                'recommendation': f'Monitor and reduce calorie intake to target range'
                            })
                            root_causes.append('Calorie intake is a primary driver of weight changes')
        
        # Analyze consistency
        if len(df) > 1:
            consistency = df['weight'].notna().sum() / len(df)
            if consistency < 0.7:
                insights.append({
                    'behavior': 'Data Consistency',
                    'impact': 'Critical',
                    'correlation': round(1 - consistency, 2),
                    'insight': f'Irregular tracking ({consistency*100:.0f}% consistency) makes it hard to identify patterns.',
                    'recommendation': 'Track your data daily for better insights'
                })
                root_causes.append('Inconsistent tracking prevents accurate pattern identification')
        
        # Identify primary root cause
        if not root_causes:
            root_causes.append('Continue tracking to identify patterns. More data needed for root cause analysis.')
        
        return {
            'insights': insights,
            'correlations': correlations,
            'root_causes': root_causes[:3],  # Top 3 root causes
            'data_points': len(health_data_list),
            'message': f'Analyzed {len(health_data_list)} data points'
        }
    
    def predict_impact(self, sleep_hours, exercise_minutes, calories, consistency):
        """Predict impact of behavior changes on weight"""
        features = np.array([[
            sleep_hours if sleep_hours else 7,
            exercise_minutes if exercise_minutes else 30,
            calories if calories else 2000,
            consistency if consistency else 0.7
        ]])
        
        predicted_change = self.model.predict(features)[0]
        return round(predicted_change, 2)

