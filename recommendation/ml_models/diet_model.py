"""
Diet Recommendation ML Model
Uses Random Forest and Linear Regression for personalized diet recommendations
"""
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
import joblib
import os
from django.conf import settings


class DietRecommendationModel:
    """ML model for diet recommendations"""
    
    def __init__(self):
        self.model = None
        self.calorie_model = None
        self.model_path = os.path.join(settings.BASE_DIR, 'recommendation', 'ml_models', 'diet_model.pkl')
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
        # Generate synthetic training data
        np.random.seed(42)
        n_samples = 1000
        
        # Features: [age, weight, height, activity_level_encoded, gender_encoded, goal_encoded]
        X = np.random.rand(n_samples, 6)
        X[:, 0] = np.random.randint(18, 70, n_samples)  # age
        X[:, 1] = np.random.uniform(50, 120, n_samples)  # weight
        X[:, 2] = np.random.uniform(150, 200, n_samples)  # height
        X[:, 3] = np.random.randint(0, 5, n_samples)  # activity level
        X[:, 4] = np.random.randint(0, 3, n_samples)  # gender
        X[:, 5] = np.random.randint(0, 4, n_samples)  # goal
        
        # Target: optimal daily calories
        y = 2000 + (X[:, 1] * 10) + (X[:, 2] * 2) - (X[:, 0] * 5) + (X[:, 3] * 200) + np.random.normal(0, 100, n_samples)
        
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.model.fit(X, y)
        
        # Save model
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump(self.model, self.model_path)
    
    def predict_calories(self, age, weight, height, activity_level, gender, goal):
        """Predict optimal daily calorie intake"""
        activity_map = {'sedentary': 0, 'light': 1, 'moderate': 2, 'active': 3, 'very_active': 4}
        gender_map = {'M': 0, 'F': 1, 'O': 2}
        goal_map = {'weight_loss': 0, 'muscle_gain': 1, 'maintenance': 2, 'general': 3}
        
        features = np.array([[
            age,
            weight,
            height,
            activity_map.get(activity_level, 0),
            gender_map.get(gender, 0),
            goal_map.get(goal, 3)
        ]])
        
        predicted_calories = self.model.predict(features)[0]
        
        # Adjust based on goal
        if goal == 'weight_loss':
            predicted_calories *= 0.85  # 15% deficit
        elif goal == 'muscle_gain':
            predicted_calories *= 1.15  # 15% surplus
        
        return max(1200, min(4000, round(predicted_calories, 0)))  # Clamp between 1200-4000
    
    def get_macronutrients(self, calories, goal):
        """Calculate macronutrient distribution"""
        if goal == 'weight_loss':
            protein_pct = 0.30
            carbs_pct = 0.35
            fats_pct = 0.35
        elif goal == 'muscle_gain':
            protein_pct = 0.35
            carbs_pct = 0.40
            fats_pct = 0.25
        else:  # maintenance or general
            protein_pct = 0.25
            carbs_pct = 0.45
            fats_pct = 0.30
        
        protein_cal = calories * protein_pct
        carbs_cal = calories * carbs_pct
        fats_cal = calories * fats_pct
        
        return {
            'protein_grams': round(protein_cal / 4, 1),
            'carbs_grams': round(carbs_cal / 4, 1),
            'fats_grams': round(fats_cal / 9, 1),
            'protein_percent': round(protein_pct * 100),
            'carbs_percent': round(carbs_pct * 100),
            'fats_percent': round(fats_pct * 100),
        }
    
    def generate_meal_plan(self, calories, dietary_preference, allergies_list):
        """Generate sample meal plan"""
        meals = {
            'breakfast': [],
            'lunch': [],
            'dinner': [],
            'snacks': []
        }
        
        # Sample food database (simplified) - Indian style breakfasts added
        food_db = {
            'none': {
                'breakfast': [
                    # Indian Breakfast Options
                    {'name': 'Poha (Flattened Rice) with vegetables', 'calories': 320, 'protein': 8, 'carbs': 60, 'fats': 8},
                    {'name': 'Upma (Semolina) with vegetables', 'calories': 350, 'protein': 10, 'carbs': 65, 'fats': 10},
                    {'name': 'Paratha with curd and pickle', 'calories': 380, 'protein': 12, 'carbs': 55, 'fats': 15},
                    {'name': 'Idli with sambar and chutney', 'calories': 300, 'protein': 10, 'carbs': 58, 'fats': 6},
                    {'name': 'Dosa with sambar', 'calories': 340, 'protein': 9, 'carbs': 62, 'fats': 8},
                    {'name': 'Aloo Paratha with butter', 'calories': 420, 'protein': 11, 'carbs': 60, 'fats': 18},
                    {'name': 'Besan Chilla (Gram flour pancake)', 'calories': 280, 'protein': 14, 'carbs': 40, 'fats': 10},
                    {'name': 'Moong Dal Cheela with vegetables', 'calories': 290, 'protein': 15, 'carbs': 38, 'fats': 9},
                    {'name': 'Rava Upma with peanuts', 'calories': 360, 'protein': 11, 'carbs': 68, 'fats': 11},
                    {'name': 'Vermicelli Upma (Semiya)', 'calories': 330, 'protein': 8, 'carbs': 64, 'fats': 9},
                    # Western Options (kept for variety)
                    {'name': 'Oatmeal with fruits', 'calories': 300, 'protein': 8, 'carbs': 55, 'fats': 6},
                    {'name': 'Scrambled eggs with toast', 'calories': 350, 'protein': 18, 'carbs': 30, 'fats': 15},
                    {'name': 'Greek yogurt with berries', 'calories': 250, 'protein': 15, 'carbs': 30, 'fats': 5},
                ],
                'lunch': [
                    {'name': 'Grilled chicken salad', 'calories': 400, 'protein': 35, 'carbs': 20, 'fats': 18},
                    {'name': 'Salmon with vegetables', 'calories': 450, 'protein': 30, 'carbs': 25, 'fats': 22},
                    {'name': 'Quinoa bowl with vegetables', 'calories': 380, 'protein': 12, 'carbs': 60, 'fats': 10},
                ],
                'dinner': [
                    {'name': 'Lean beef with sweet potato', 'calories': 500, 'protein': 40, 'carbs': 45, 'fats': 15},
                    {'name': 'Baked fish with rice', 'calories': 420, 'protein': 35, 'carbs': 50, 'fats': 12},
                    {'name': 'Turkey stir-fry', 'calories': 450, 'protein': 38, 'carbs': 40, 'fats': 16},
                ],
            },
            'vegetarian': {
                'breakfast': [
                    # Indian Vegetarian Breakfast Options
                    {'name': 'Poha with peanuts and vegetables', 'calories': 320, 'protein': 9, 'carbs': 62, 'fats': 9},
                    {'name': 'Upma with vegetables and cashews', 'calories': 360, 'protein': 11, 'carbs': 67, 'fats': 11},
                    {'name': 'Aloo Paratha with curd', 'calories': 400, 'protein': 12, 'carbs': 58, 'fats': 16},
                    {'name': 'Idli with sambar and coconut chutney', 'calories': 310, 'protein': 11, 'carbs': 60, 'fats': 7},
                    {'name': 'Masala Dosa with sambar', 'calories': 350, 'protein': 10, 'carbs': 64, 'fats': 9},
                    {'name': 'Besan Chilla with mint chutney', 'calories': 290, 'protein': 15, 'carbs': 42, 'fats': 11},
                    {'name': 'Moong Dal Cheela with tomato chutney', 'calories': 300, 'protein': 16, 'carbs': 40, 'fats': 10},
                    {'name': 'Rava Idli with sambar', 'calories': 320, 'protein': 10, 'carbs': 61, 'fats': 8},
                    {'name': 'Vegetable Paratha with pickle', 'calories': 380, 'protein': 11, 'carbs': 56, 'fats': 15},
                    {'name': 'Vermicelli Upma with vegetables', 'calories': 340, 'protein': 9, 'carbs': 66, 'fats': 10},
                    # Western Options
                    {'name': 'Vegetable omelet', 'calories': 280, 'protein': 15, 'carbs': 20, 'fats': 16},
                    {'name': 'Avocado toast', 'calories': 320, 'protein': 10, 'carbs': 40, 'fats': 14},
                ],
                'lunch': [
                    {'name': 'Lentil curry with rice', 'calories': 420, 'protein': 18, 'carbs': 65, 'fats': 10},
                    {'name': 'Chickpea salad', 'calories': 380, 'protein': 16, 'carbs': 50, 'fats': 12},
                ],
                'dinner': [
                    {'name': 'Tofu stir-fry', 'calories': 400, 'protein': 20, 'carbs': 45, 'fats': 14},
                    {'name': 'Vegetable pasta', 'calories': 450, 'protein': 12, 'carbs': 70, 'fats': 12},
                ],
            },
            'vegan': {
                'breakfast': [
                    {'name': 'Smoothie bowl', 'calories': 300, 'protein': 8, 'carbs': 60, 'fats': 6},
                    {'name': 'Avocado toast', 'calories': 320, 'protein': 10, 'carbs': 40, 'fats': 14},
                ],
                'lunch': [
                    {'name': 'Quinoa salad', 'calories': 400, 'protein': 14, 'carbs': 65, 'fats': 10},
                    {'name': 'Lentil soup', 'calories': 350, 'protein': 16, 'carbs': 55, 'fats': 8},
                ],
                'dinner': [
                    {'name': 'Vegan curry with rice', 'calories': 450, 'protein': 12, 'carbs': 75, 'fats': 12},
                    {'name': 'Stuffed bell peppers', 'calories': 380, 'protein': 10, 'carbs': 60, 'fats': 10},
                ],
            },
        }
        
        preference = dietary_preference if dietary_preference in food_db else 'none'
        food_options = food_db[preference]
        
        # Select meals (simplified - in production, use more sophisticated algorithm)
        import random
        if food_options.get('breakfast'):
            meals['breakfast'] = random.choice(food_options['breakfast'])
        if food_options.get('lunch'):
            meals['lunch'] = random.choice(food_options['lunch'])
        if food_options.get('dinner'):
            meals['dinner'] = random.choice(food_options['dinner'])
        
        meals['snacks'] = [
            {'name': 'Apple with almond butter', 'calories': 200, 'protein': 5, 'carbs': 25, 'fats': 10},
            {'name': 'Mixed nuts', 'calories': 150, 'protein': 5, 'carbs': 5, 'fats': 12},
        ]
        
        return meals

