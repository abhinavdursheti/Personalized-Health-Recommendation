"""
Exercise Recommendation ML Model
Uses Decision Tree and Clustering for personalized exercise recommendations
"""
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.cluster import KMeans
import joblib
import os
from django.conf import settings


class ExerciseRecommendationModel:
    """ML model for exercise recommendations"""
    
    def __init__(self):
        self.model = None
        self.model_path = os.path.join(settings.BASE_DIR, 'recommendation', 'ml_models', 'exercise_model.pkl')
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
        
        # Features: [fitness_level, goal_encoded, available_time, age, bmi]
        X = np.random.rand(n_samples, 5)
        X[:, 0] = np.random.randint(0, 3, n_samples)  # fitness level (0=beginner, 1=intermediate, 2=advanced)
        X[:, 1] = np.random.randint(0, 4, n_samples)  # goal
        X[:, 2] = np.random.randint(20, 120, n_samples)  # available time (minutes)
        X[:, 3] = np.random.randint(18, 65, n_samples)  # age
        X[:, 4] = np.random.uniform(18, 35, n_samples)  # BMI
        
        # Target: exercise type (0=cardio, 1=strength, 2=mixed, 3=flexibility)
        y = np.random.randint(0, 4, n_samples)
        
        self.model = DecisionTreeClassifier(random_state=42, max_depth=10)
        self.model.fit(X, y)
        
        # Save model
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump(self.model, self.model_path)
    
    def get_fitness_level(self, activity_level, age, bmi):
        """Determine fitness level based on user data"""
        if activity_level in ['sedentary', 'light']:
            return 'beginner'
        elif activity_level == 'moderate':
            return 'intermediate'
        else:
            return 'advanced'
    
    def recommend_exercises(self, fitness_level, goal, available_time, age, bmi):
        """Generate exercise recommendations"""
        fitness_map = {'beginner': 0, 'intermediate': 1, 'advanced': 2}
        goal_map = {'weight_loss': 0, 'muscle_gain': 1, 'maintenance': 2, 'general': 3}
        
        features = np.array([[
            fitness_map.get(fitness_level, 0),
            goal_map.get(goal, 3),
            available_time,
            age,
            bmi
        ]])
        
        exercise_type = self.model.predict(features)[0]
        
        # Exercise database - Expanded with more options
        exercises = {
            'beginner': {
                'cardio': [
                    {'name': 'Brisk Walking', 'duration': 30, 'intensity': 'Low', 'calories': 150},
                    {'name': 'Cycling (Easy)', 'duration': 25, 'intensity': 'Low', 'calories': 120},
                    {'name': 'Swimming (Leisurely)', 'duration': 20, 'intensity': 'Low', 'calories': 100},
                    {'name': 'Jogging (Slow pace)', 'duration': 20, 'intensity': 'Low', 'calories': 140},
                    {'name': 'Dancing', 'duration': 25, 'intensity': 'Low', 'calories': 130},
                    {'name': 'Stair Climbing', 'duration': 15, 'intensity': 'Low', 'calories': 110},
                    {'name': 'Elliptical Trainer', 'duration': 25, 'intensity': 'Low', 'calories': 125},
                    {'name': 'Yoga Flow', 'duration': 30, 'intensity': 'Low', 'calories': 90},
                    {'name': 'Tai Chi', 'duration': 30, 'intensity': 'Low', 'calories': 80},
                    {'name': 'Pilates', 'duration': 30, 'intensity': 'Low', 'calories': 100},
                    {'name': 'Water Aerobics', 'duration': 30, 'intensity': 'Low', 'calories': 120},
                    {'name': 'Hiking (Easy trail)', 'duration': 40, 'intensity': 'Low', 'calories': 180},
                ],
                'strength': [
                    {'name': 'Bodyweight Squats', 'sets': 3, 'reps': 10, 'intensity': 'Low'},
                    {'name': 'Push-ups (Knee)', 'sets': 3, 'reps': 8, 'intensity': 'Low'},
                    {'name': 'Plank', 'duration': 30, 'intensity': 'Low'},
                    {'name': 'Wall Push-ups', 'sets': 3, 'reps': 12, 'intensity': 'Low'},
                    {'name': 'Lunges', 'sets': 2, 'reps': 8, 'intensity': 'Low'},
                    {'name': 'Glute Bridges', 'sets': 3, 'reps': 12, 'intensity': 'Low'},
                    {'name': 'Bird Dog', 'sets': 2, 'reps': 10, 'intensity': 'Low'},
                    {'name': 'Modified Burpees', 'sets': 2, 'reps': 5, 'intensity': 'Low'},
                    {'name': 'Calf Raises', 'sets': 3, 'reps': 15, 'intensity': 'Low'},
                    {'name': 'Leg Raises', 'sets': 2, 'reps': 10, 'intensity': 'Low'},
                    {'name': 'Superman', 'sets': 2, 'reps': 10, 'intensity': 'Low'},
                    {'name': 'Wall Sit', 'duration': 30, 'intensity': 'Low'},
                ],
                'mixed': [
                    {'name': 'Full Body Circuit', 'duration': 20, 'intensity': 'Low', 'exercises': ['Squats', 'Push-ups', 'Lunges']},
                    {'name': 'Beginner HIIT', 'duration': 15, 'intensity': 'Low', 'exercises': ['Jumping Jacks', 'Squats', 'Plank']},
                    {'name': 'Yoga Strength Flow', 'duration': 25, 'intensity': 'Low', 'exercises': ['Warrior Poses', 'Plank', 'Downward Dog']},
                ],
            },
            'intermediate': {
                'cardio': [
                    {'name': 'Running (Moderate)', 'duration': 30, 'intensity': 'Moderate', 'calories': 300},
                    {'name': 'Cycling (Moderate)', 'duration': 35, 'intensity': 'Moderate', 'calories': 280},
                    {'name': 'HIIT Workout', 'duration': 25, 'intensity': 'High', 'calories': 350},
                    {'name': 'Rowing Machine', 'duration': 25, 'intensity': 'Moderate', 'calories': 290},
                    {'name': 'Jump Rope', 'duration': 20, 'intensity': 'Moderate', 'calories': 250},
                    {'name': 'Swimming Laps', 'duration': 30, 'intensity': 'Moderate', 'calories': 320},
                    {'name': 'Treadmill Running', 'duration': 30, 'intensity': 'Moderate', 'calories': 310},
                    {'name': 'Dance Cardio', 'duration': 30, 'intensity': 'Moderate', 'calories': 280},
                    {'name': 'Kickboxing', 'duration': 30, 'intensity': 'Moderate', 'calories': 350},
                    {'name': 'Zumba', 'duration': 30, 'intensity': 'Moderate', 'calories': 300},
                    {'name': 'Spinning Class', 'duration': 30, 'intensity': 'Moderate', 'calories': 320},
                    {'name': 'StairMaster', 'duration': 25, 'intensity': 'Moderate', 'calories': 290},
                    {'name': 'Rowing (Moderate)', 'duration': 30, 'intensity': 'Moderate', 'calories': 310},
                    {'name': 'Aerobics Class', 'duration': 30, 'intensity': 'Moderate', 'calories': 280},
                ],
                'strength': [
                    {'name': 'Squats', 'sets': 4, 'reps': 12, 'intensity': 'Moderate'},
                    {'name': 'Push-ups', 'sets': 4, 'reps': 15, 'intensity': 'Moderate'},
                    {'name': 'Deadlifts', 'sets': 3, 'reps': 10, 'intensity': 'Moderate'},
                    {'name': 'Pull-ups/Chin-ups', 'sets': 3, 'reps': 8, 'intensity': 'Moderate'},
                    {'name': 'Dumbbell Rows', 'sets': 3, 'reps': 12, 'intensity': 'Moderate'},
                    {'name': 'Overhead Press', 'sets': 3, 'reps': 10, 'intensity': 'Moderate'},
                    {'name': 'Lunges (Weighted)', 'sets': 3, 'reps': 12, 'intensity': 'Moderate'},
                    {'name': 'Bench Press', 'sets': 3, 'reps': 10, 'intensity': 'Moderate'},
                    {'name': 'Leg Press', 'sets': 3, 'reps': 15, 'intensity': 'Moderate'},
                    {'name': 'Bicep Curls', 'sets': 3, 'reps': 12, 'intensity': 'Moderate'},
                    {'name': 'Tricep Dips', 'sets': 3, 'reps': 10, 'intensity': 'Moderate'},
                    {'name': 'Shoulder Press', 'sets': 3, 'reps': 10, 'intensity': 'Moderate'},
                    {'name': 'Chest Flyes', 'sets': 3, 'reps': 12, 'intensity': 'Moderate'},
                    {'name': 'Leg Curls', 'sets': 3, 'reps': 12, 'intensity': 'Moderate'},
                    {'name': 'Calf Raises (Weighted)', 'sets': 3, 'reps': 15, 'intensity': 'Moderate'},
                ],
                'mixed': [
                    {'name': 'CrossFit-style Workout', 'duration': 30, 'intensity': 'Moderate'},
                    {'name': 'Circuit Training', 'duration': 30, 'intensity': 'Moderate', 'exercises': ['Squats', 'Push-ups', 'Burpees', 'Plank']},
                    {'name': 'Tabata Workout', 'duration': 20, 'intensity': 'High', 'exercises': ['Squat Jumps', 'Push-ups', 'Mountain Climbers']},
                    {'name': 'Full Body Strength + Cardio', 'duration': 35, 'intensity': 'Moderate'},
                ],
            },
            'advanced': {
                'cardio': [
                    {'name': 'Running (Fast)', 'duration': 40, 'intensity': 'High', 'calories': 500},
                    {'name': 'Cycling (Intense)', 'duration': 45, 'intensity': 'High', 'calories': 450},
                    {'name': 'HIIT Advanced', 'duration': 30, 'intensity': 'Very High', 'calories': 600},
                    {'name': 'Sprint Intervals', 'duration': 25, 'intensity': 'Very High', 'calories': 550},
                    {'name': 'Rowing (Intense)', 'duration': 30, 'intensity': 'High', 'calories': 480},
                    {'name': 'Swimming (Intense)', 'duration': 35, 'intensity': 'High', 'calories': 500},
                    {'name': 'Boxing Training', 'duration': 40, 'intensity': 'High', 'calories': 550},
                    {'name': 'Mountain Biking', 'duration': 45, 'intensity': 'High', 'calories': 520},
                    {'name': 'Trail Running', 'duration': 45, 'intensity': 'High', 'calories': 530},
                    {'name': 'Spin Class (Intense)', 'duration': 40, 'intensity': 'High', 'calories': 500},
                    {'name': 'MMA Training', 'duration': 40, 'intensity': 'Very High', 'calories': 580},
                    {'name': 'CrossFit Cardio', 'duration': 30, 'intensity': 'Very High', 'calories': 600},
                ],
                'strength': [
                    {'name': 'Weighted Squats', 'sets': 5, 'reps': 8, 'intensity': 'High'},
                    {'name': 'Bench Press', 'sets': 4, 'reps': 6, 'intensity': 'High'},
                    {'name': 'Deadlifts (Heavy)', 'sets': 4, 'reps': 5, 'intensity': 'High'},
                    {'name': 'Barbell Rows', 'sets': 4, 'reps': 8, 'intensity': 'High'},
                    {'name': 'Overhead Press (Heavy)', 'sets': 4, 'reps': 6, 'intensity': 'High'},
                    {'name': 'Pull-ups (Weighted)', 'sets': 4, 'reps': 8, 'intensity': 'High'},
                    {'name': 'Leg Press (Heavy)', 'sets': 4, 'reps': 10, 'intensity': 'High'},
                    {'name': 'Romanian Deadlifts', 'sets': 4, 'reps': 8, 'intensity': 'High'},
                    {'name': 'Dips (Weighted)', 'sets': 4, 'reps': 8, 'intensity': 'High'},
                    {'name': 'Barbell Curls', 'sets': 4, 'reps': 8, 'intensity': 'High'},
                    {'name': 'Front Squats', 'sets': 4, 'reps': 6, 'intensity': 'High'},
                    {'name': 'Incline Bench Press', 'sets': 4, 'reps': 8, 'intensity': 'High'},
                    {'name': 'Barbell Hip Thrusts', 'sets': 4, 'reps': 8, 'intensity': 'High'},
                    {'name': 'Military Press', 'sets': 4, 'reps': 6, 'intensity': 'High'},
                    {'name': 'T-Bar Rows', 'sets': 4, 'reps': 8, 'intensity': 'High'},
                ],
                'mixed': [
                    {'name': 'Advanced Circuit Training', 'duration': 40, 'intensity': 'High'},
                    {'name': 'CrossFit WOD', 'duration': 30, 'intensity': 'Very High', 'exercises': ['Thrusters', 'Pull-ups', 'Box Jumps']},
                    {'name': 'Advanced HIIT', 'duration': 35, 'intensity': 'Very High', 'exercises': ['Burpees', 'Sprint', 'Kettlebell Swings']},
                    {'name': 'Powerlifting + Cardio', 'duration': 45, 'intensity': 'High'},
                ],
            },
        }
        
        # Select exercises based on goal and type
        if goal == 'weight_loss':
            exercise_category = 'cardio'
        elif goal == 'muscle_gain':
            exercise_category = 'strength'
        else:
            exercise_category = 'mixed'
        
        available_exercises = exercises.get(fitness_level, exercises['beginner']).get(exercise_category, [])
        
        # Select exercises that fit within available time
        selected = []
        total_time = 0
        for ex in available_exercises:
            ex_time = ex.get('duration', 15)
            if total_time + ex_time <= available_time:
                selected.append(ex)
                total_time += ex_time
            if len(selected) >= 5:  # Increased limit to 5 exercises
                break
        
        if not selected and available_exercises:
            selected = [available_exercises[0]]  # At least one exercise
        
        return {
            'fitness_level': fitness_level,
            'exercise_type': exercise_category,
            'exercises': selected,
            'total_duration': total_time,
            'frequency': self._get_frequency(goal, fitness_level),
        }
    
    def _get_frequency(self, goal, fitness_level):
        """Get recommended workout frequency"""
        if goal == 'weight_loss':
            return '5-6 times per week'
        elif goal == 'muscle_gain':
            return '4-5 times per week (with rest days)'
        else:
            return '3-4 times per week'

