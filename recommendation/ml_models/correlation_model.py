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
        # Relax the initial filtering to ensure we calculate actual correlations
        if not health_data_list or len(health_data_list) < 2:
            return {
                'insights': [],
                'correlations': {},
                'root_causes': ['Not enough data. Please log at least 2 days of data to see correlations.'],
                'data_points': len(health_data_list),
                'message': f'Analyzed {len(health_data_list)} data points'
            }
        
        # Prepare data
        data = []
        for entry in health_data_list:
            data.append({
                'date': entry.date,
                'weight': entry.weight,
                'sleep_hours': entry.sleep_hours if entry.sleep_hours is not None else np.nan,
                'exercise_minutes': entry.exercise_minutes if entry.exercise_minutes is not None else np.nan,
                'calories_consumed': entry.calories_consumed if entry.calories_consumed is not None else np.nan,
            })
        
        df = pd.DataFrame(data)
        df = df.sort_values('date').reset_index(drop=True)
        
        # Calculate daily weight change, allowing for overall drift understanding
        df['weight_change'] = df['weight'].diff().fillna(0)
        
        # In a real scenario, health data has many missing values.
        # We'll forward-fill numerical features up to 3 days to establish a trend, then drop remaining NaNs.
        df[['sleep_hours', 'exercise_minutes', 'calories_consumed']] = df[['sleep_hours', 'exercise_minutes', 'calories_consumed']].ffill(limit=3)
        df[['sleep_hours', 'exercise_minutes', 'calories_consumed']] = df[['sleep_hours', 'exercise_minutes', 'calories_consumed']].bfill(limit=1)
        
        # Calculate correlations vs weight (not weight_change, as the user wants general trends)
        # Weight change could also be used depending on the exact health philosophy. 
        # Using pure 'weight' matches the examples: "sleep_hours vs weight"
        
        insights = []
        correlations = {}
        root_causes = []
        
        def add_insight(behavior, aspect, corr_val, target_col):
            # Dynamic correlation thresholds
            if corr_val < -0.5:
                # Strong negative
                msg = f"Higher {behavior.lower()} tracking appears associated with lower {target_col.lower()}"
                impact = "Positive" if "weight" in target_col else "Negative"
                rec = f"Continue optimizing your {behavior.lower()}"
                insights.append({'behavior': behavior, 'impact': impact, 'correlation': round(corr_val, 2), 'insight': msg, 'recommendation': rec})
                root_causes.append(f"Strong inverse relationship detected between {behavior.lower()} and {target_col.lower()}")
            elif corr_val < -0.2:
                # Weak negative
                msg = f"Slight tendency for {target_col.lower()} to decrease when {behavior.lower()} increases"
                insights.append({'behavior': behavior, 'impact': 'Neutral', 'correlation': round(corr_val, 2), 'insight': msg, 'recommendation': f"Monitor your {behavior.lower()} for further changes."})
            elif corr_val > 0.5:
                # Strong positive
                msg = f"Higher {behavior.lower()} tracking appears linked to higher {target_col.lower()}"
                impact = "Negative" if "weight" in target_col else "Positive"
                rec = f"Review your {behavior.lower()} targets"
                insights.append({'behavior': behavior, 'impact': impact, 'correlation': round(corr_val, 2), 'insight': msg, 'recommendation': rec})
                root_causes.append(f"Strong direct relationship detected between {behavior.lower()} and {target_col.lower()}")
            elif corr_val > 0.2:
                # Weak positive
                msg = f"Slight tendency for {target_col.lower()} to increase alongside {behavior.lower()}"
                insights.append({'behavior': behavior, 'impact': 'Neutral', 'correlation': round(corr_val, 2), 'insight': msg, 'recommendation': f"Keep an eye on how {behavior.lower()} affects your {target_col.lower()}"})
            else:
                pass # Between -0.2 and 0.2: "No strong behavioral correlation detected."
        
        # Helper string formats
        feature_names = {
            'sleep_hours': 'Sleep duration',
            'exercise_minutes': 'Exercise frequency',
            'calories_consumed': 'Calorie intake'
        }

        # Calculate Pearson correlation for valid pairs
        def calc_corr(col1, col2):
            valid_df = df.dropna(subset=[col1, col2])
            if len(valid_df) >= 3: # Need at least 3 points for a meaningful correlation
                return valid_df[col1].corr(valid_df[col2])
            return np.nan
        
        # Analyze sleep vs weight
        corr_sleep_weight = calc_corr('sleep_hours', 'weight')
        if not np.isnan(corr_sleep_weight):
            correlations['sleep_hours_vs_weight'] = round(corr_sleep_weight, 3)
            add_insight(feature_names['sleep_hours'], 'sleep', corr_sleep_weight, 'Weight')
        
        # Analyze exercise vs weight
        corr_ex_weight = calc_corr('exercise_minutes', 'weight')
        if not np.isnan(corr_ex_weight):
            correlations['exercise_minutes_vs_weight'] = round(corr_ex_weight, 3)
            add_insight(feature_names['exercise_minutes'], 'exercise', corr_ex_weight, 'Weight')
            
        # Analyze calories vs weight
        corr_cal_weight = calc_corr('calories_consumed', 'weight')
        if not np.isnan(corr_cal_weight):
            correlations['calories_consumed_vs_weight'] = round(corr_cal_weight, 3)
            if corr_cal_weight > 0.5:
                insights.append({
                    'behavior': 'Calories Consumed',
                    'impact': 'Negative',
                    'correlation': round(corr_cal_weight, 2),
                    'insight': 'Higher calorie intake appears linked to weight gain.',
                    'recommendation': 'Monitor and reduce calorie intake consistently.'
                })
                root_causes.append('Calorie intake is a primary driver of observed weight changes.')
            elif corr_cal_weight < -0.5:
                insights.append({
                    'behavior': 'Calories Consumed',
                    'impact': 'Positive',
                    'correlation': round(corr_cal_weight, 2),
                    'insight': 'Lower calorie intake appears linked to weight loss.',
                    'recommendation': 'You are maintaining a healthy deficit.'
                })
            else:
                add_insight(feature_names['calories_consumed'], 'calories', corr_cal_weight, 'Weight')
                
        # Analyze exercise vs sleep (secondary insight)
        corr_ex_sleep = calc_corr('exercise_minutes', 'sleep_hours')
        if not np.isnan(corr_ex_sleep):
            correlations['exercise_minutes_vs_sleep'] = round(corr_ex_sleep, 3)
            if corr_ex_sleep > 0.4:
                insights.append({
                    'behavior': 'Exercise & Sleep',
                    'impact': 'Positive',
                    'correlation': round(corr_ex_sleep, 2),
                    'insight': 'Days with more exercise often correspond to longer sleep.',
                    'recommendation': 'Keep exercising to maintain good sleep hygiene.'
                })
        
        # Identify strongest correlation
        strongest_factor = None
        strongest_val = -1
        for key, val in correlations.items():
            if abs(val) > strongest_val:
                strongest_val = abs(val)
                strongest_factor = key
                
        # Fallback if no strong correlations found despite having enough data points
        if strongest_val <= 0.2 and len(df) >= 3:
             insights.append({
                    'behavior': 'General Trends',
                    'impact': 'Neutral',
                    'correlation': 0.0,
                    'insight': 'No strong behavioral correlation detected.',
                    'recommendation': 'Keep logging your data. Stronger patterns may emerge over a longer period.'
                })
             root_causes.append('Current data does not clearly point out a single strongest root cause. Continue monitoring.')
             
        # Add primary root cause emphasis (deduplicate)
        root_causes = list(dict.fromkeys(root_causes))
        if len(root_causes) == 0:
            root_causes.append("Gathering more data points will help uncover underlying causes.")
            
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

