"""
Personalized Habit Sensitivity Analyzer
Analyzes which habits are fragile vs resilient and their impact
"""
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
import joblib
import os
from django.conf import settings
from datetime import datetime, timedelta


class HabitSensitivityModel:
    """ML model for analyzing habit sensitivity and fragility"""
    
    def __init__(self):
        self.fragility_model = None
        self.impact_model = None
        self.scaler = StandardScaler()
        self.fragility_model_path = os.path.join(settings.BASE_DIR, 'recommendation', 'ml_models', 'fragility_model.pkl')
        self.impact_model_path = os.path.join(settings.BASE_DIR, 'recommendation', 'ml_models', 'impact_model.pkl')
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize or load the models"""
        if os.path.exists(self.fragility_model_path) and os.path.exists(self.impact_model_path):
            try:
                self.fragility_model = joblib.load(self.fragility_model_path)
                self.impact_model = joblib.load(self.impact_model_path)
            except:
                self._train_models()
        else:
            self._train_models()
    
    def _train_models(self):
        """Train the models with synthetic data"""
        np.random.seed(42)
        n_samples = 800
        
        # Features: [habit_type, duration_days, frequency, complexity, support_level, personal_relevance]
        X = np.random.rand(n_samples, 6)
        X[:, 0] = np.random.randint(0, 4, n_samples)  # habit_type (0=diet, 1=exercise, 2=sleep, 3=tracking)
        X[:, 1] = np.random.randint(1, 180, n_samples)  # duration_days
        X[:, 2] = np.random.uniform(0.1, 1.0, n_samples)  # frequency (how often done)
        X[:, 3] = np.random.uniform(0.1, 1.0, n_samples)  # complexity (0=simple, 1=complex)
        X[:, 4] = np.random.uniform(0.1, 1.0, n_samples)  # support_level
        X[:, 5] = np.random.uniform(0.1, 1.0, n_samples)  # personal_relevance
        
        # Fragility score (0-1, higher = more fragile)
        fragility_y = (1 - X[:, 1] / 180) * 0.3 + (1 - X[:, 2]) * 0.3 + X[:, 3] * 0.2 + (1 - X[:, 4]) * 0.1 + (1 - X[:, 5]) * 0.1
        fragility_y = np.clip(fragility_y, 0, 1)
        
        # Impact score (0-1, higher = more impact on health)
        impact_y = (1 - X[:, 0] / 4) * 0.2 + X[:, 2] * 0.3 + (1 - X[:, 3]) * 0.2 + X[:, 5] * 0.3
        impact_y = np.clip(impact_y, 0, 1)
        
        # Train fragility model
        fragility_binary = (fragility_y > 0.5).astype(int)
        self.fragility_model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=8)
        self.fragility_model.fit(X, fragility_binary)
        
        # Train impact model
        self.impact_model = GradientBoostingRegressor(n_estimators=100, random_state=42, max_depth=6)
        self.impact_model.fit(X, impact_y)
        
        # Save models
        os.makedirs(os.path.dirname(self.fragility_model_path), exist_ok=True)
        joblib.dump(self.fragility_model, self.fragility_model_path)
        joblib.dump(self.impact_model, self.impact_model_path)
    
    def analyze_habits(self, health_data_list, user_profile):
        """Analyze habit sensitivity for different health behaviors"""
        if not health_data_list or len(health_data_list) < 1:
            return {
                'habits': [],
                'fragile_habits': [],
                'resilient_habits': [],
                'high_impact_habits': [],
                'message': 'Add more data points for detailed habit analysis'
            }
        
        # Calculate habit metrics
        habits = []
        
        # Analyze Diet Habit
        diet_data = [d for d in health_data_list if d.calories_consumed is not None]
        if diet_data:
            diet_frequency = len(diet_data) / len(health_data_list)
            diet_duration = (health_data_list[-1].date - health_data_list[0].date).days
            diet_consistency = self._calculate_consistency([d.date for d in diet_data])
            
            diet_fragility = self._predict_fragility(
                habit_type=0,  # diet
                duration_days=diet_duration,
                frequency=diet_frequency,
                complexity=0.6,  # Moderate complexity
                support_level=0.7,
                personal_relevance=0.8 if user_profile.health_goal in ['weight_loss', 'muscle_gain'] else 0.5
            )
            
            diet_impact = self._predict_impact(
                habit_type=0,
                duration_days=diet_duration,
                frequency=diet_frequency,
                complexity=0.6,
                support_level=0.7,
                personal_relevance=0.8 if user_profile.health_goal in ['weight_loss', 'muscle_gain'] else 0.5
            )
            
            habits.append({
                'name': 'Diet Tracking',
                'type': 'diet',
                'fragility_score': round(diet_fragility['score'] * 100, 1),
                'is_fragile': diet_fragility['is_fragile'],
                'impact_score': round(diet_impact * 100, 1),
                'frequency': round(diet_frequency * 100, 1),
                'duration_days': diet_duration,
                'consistency': round(diet_consistency * 100, 1),
                'recommendations': diet_fragility['recommendations']
            })
        
        # Analyze Exercise Habit
        exercise_data = [d for d in health_data_list if d.exercise_minutes is not None and d.exercise_minutes > 0]
        if exercise_data:
            exercise_frequency = len(exercise_data) / len(health_data_list)
            exercise_duration = (health_data_list[-1].date - health_data_list[0].date).days
            exercise_consistency = self._calculate_consistency([d.date for d in exercise_data])
            
            exercise_fragility = self._predict_fragility(
                habit_type=1,  # exercise
                duration_days=exercise_duration,
                frequency=exercise_frequency,
                complexity=0.7,  # Higher complexity
                support_level=0.6,
                personal_relevance=0.9 if user_profile.health_goal in ['muscle_gain', 'weight_loss'] else 0.6
            )
            
            exercise_impact = self._predict_impact(
                habit_type=1,
                duration_days=exercise_duration,
                frequency=exercise_frequency,
                complexity=0.7,
                support_level=0.6,
                personal_relevance=0.9 if user_profile.health_goal in ['muscle_gain', 'weight_loss'] else 0.6
            )
            
            habits.append({
                'name': 'Exercise Routine',
                'type': 'exercise',
                'fragility_score': round(exercise_fragility['score'] * 100, 1),
                'is_fragile': exercise_fragility['is_fragile'],
                'impact_score': round(exercise_impact * 100, 1),
                'frequency': round(exercise_frequency * 100, 1),
                'duration_days': exercise_duration,
                'consistency': round(exercise_consistency * 100, 1),
                'recommendations': exercise_fragility['recommendations']
            })
        
        # Analyze Sleep Habit
        sleep_data = [d for d in health_data_list if d.sleep_hours is not None]
        if sleep_data:
            sleep_frequency = len(sleep_data) / len(health_data_list)
            sleep_duration = (health_data_list[-1].date - health_data_list[0].date).days
            sleep_consistency = self._calculate_consistency([d.date for d in sleep_data])
            
            sleep_fragility = self._predict_fragility(
                habit_type=2,  # sleep
                duration_days=sleep_duration,
                frequency=sleep_frequency,
                complexity=0.3,  # Lower complexity
                support_level=0.8,
                personal_relevance=0.7
            )
            
            sleep_impact = self._predict_impact(
                habit_type=2,
                duration_days=sleep_duration,
                frequency=sleep_frequency,
                complexity=0.3,
                support_level=0.8,
                personal_relevance=0.7
            )
            
            habits.append({
                'name': 'Sleep Schedule',
                'type': 'sleep',
                'fragility_score': round(sleep_fragility['score'] * 100, 1),
                'is_fragile': sleep_fragility['is_fragile'],
                'impact_score': round(sleep_impact * 100, 1),
                'frequency': round(sleep_frequency * 100, 1),
                'duration_days': sleep_duration,
                'consistency': round(sleep_consistency * 100, 1),
                'recommendations': sleep_fragility['recommendations']
            })
        
        # Categorize habits
        fragile_habits = [h for h in habits if h['is_fragile']]
        resilient_habits = [h for h in habits if not h['is_fragile']]
        high_impact_habits = sorted(habits, key=lambda x: x['impact_score'], reverse=True)[:2]
        
        return {
            'habits': habits,
            'fragile_habits': fragile_habits,
            'resilient_habits': resilient_habits,
            'high_impact_habits': high_impact_habits,
            'total_habits': len(habits),
            'message': f'Analyzed {len(habits)} habits from {len(health_data_list)} data points'
        }
    
    def _calculate_consistency(self, dates):
        """Calculate consistency score from dates"""
        if len(dates) < 2:
            return 0.5
        
        dates = sorted(dates)
        intervals = [(dates[i] - dates[i-1]).days for i in range(1, len(dates))]
        avg_interval = np.mean(intervals) if intervals else 1
        consistency = 1.0 / (1.0 + avg_interval) if avg_interval > 0 else 1.0
        return min(1.0, consistency * 2)
    
    def _predict_fragility(self, habit_type, duration_days, frequency, complexity, support_level, personal_relevance):
        """Predict if a habit is fragile"""
        features = np.array([[
            habit_type,
            min(duration_days, 180),
            frequency,
            complexity,
            support_level,
            personal_relevance
        ]])
        
        is_fragile = self.fragility_model.predict(features)[0]
        fragility_prob = self.fragility_model.predict_proba(features)[0]
        fragility_score = fragility_prob[1] if len(fragility_prob) > 1 else fragility_prob[0]
        
        recommendations = []
        if is_fragile:
            if frequency < 0.5:
                recommendations.append("Increase frequency - aim for daily practice")
            if complexity > 0.6:
                recommendations.append("Simplify the habit - break into smaller steps")
            if support_level < 0.6:
                recommendations.append("Build support system or accountability")
            if duration_days < 30:
                recommendations.append("Habit needs more time to establish (aim for 30+ days)")
        else:
            recommendations.append("Habit is well-established - maintain consistency")
            if frequency < 0.8:
                recommendations.append("Consider increasing frequency for better results")
        
        return {
            'is_fragile': bool(is_fragile),
            'score': fragility_score,
            'recommendations': recommendations
        }
    
    def _predict_impact(self, habit_type, duration_days, frequency, complexity, support_level, personal_relevance):
        """Predict impact score of a habit"""
        features = np.array([[
            habit_type,
            min(duration_days, 180),
            frequency,
            complexity,
            support_level,
            personal_relevance
        ]])
        
        impact = self.impact_model.predict(features)[0]
        return max(0, min(1, impact))

