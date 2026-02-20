"""
Food Database with Nutritional Information
Contains common foods with their nutritional values per serving/100g
"""
FOOD_DATABASE = {
    # Indian Breakfast Items
    'Poha (Flattened Rice)': {
        'calories_per_100g': 350,
        'protein_per_100g': 7,
        'carbs_per_100g': 77,
        'fats_per_100g': 0.5,
        'fiber_per_100g': 1.5,
        'serving_size': 100,  # grams
    },
    'Upma (Semolina)': {
        'calories_per_100g': 360,
        'protein_per_100g': 10,
        'carbs_per_100g': 73,
        'fats_per_100g': 1.5,
        'fiber_per_100g': 2,
        'serving_size': 100,
    },
    'Idli': {
        'calories_per_100g': 100,
        'protein_per_100g': 3,
        'carbs_per_100g': 20,
        'fats_per_100g': 0.2,
        'fiber_per_100g': 1,
        'serving_size': 50,  # 2 idlis
    },
    'Dosa': {
        'calories_per_100g': 150,
        'protein_per_100g': 4,
        'carbs_per_100g': 25,
        'fats_per_100g': 3,
        'fiber_per_100g': 1.5,
        'serving_size': 100,  # 1 dosa
    },
    'Paratha': {
        'calories_per_100g': 300,
        'protein_per_100g': 8,
        'carbs_per_100g': 45,
        'fats_per_100g': 10,
        'fiber_per_100g': 2,
        'serving_size': 100,  # 1 paratha
    },
    'Aloo Paratha': {
        'calories_per_100g': 350,
        'protein_per_100g': 9,
        'carbs_per_100g': 50,
        'fats_per_100g': 12,
        'fiber_per_100g': 3,
        'serving_size': 100,
    },
    'Besan Chilla': {
        'calories_per_100g': 200,
        'protein_per_100g': 12,
        'carbs_per_100g': 25,
        'fats_per_100g': 6,
        'fiber_per_100g': 5,
        'serving_size': 100,
    },
    'Moong Dal Cheela': {
        'calories_per_100g': 180,
        'protein_per_100g': 13,
        'carbs_per_100g': 22,
        'fats_per_100g': 4,
        'fiber_per_100g': 6,
        'serving_size': 100,
    },
    
    # Indian Lunch/Dinner Items
    'Dal (Lentils)': {
        'calories_per_100g': 120,
        'protein_per_100g': 7,
        'carbs_per_100g': 20,
        'fats_per_100g': 0.5,
        'fiber_per_100g': 8,
        'serving_size': 150,  # 1 katori
    },
    'Rice (Cooked)': {
        'calories_per_100g': 130,
        'protein_per_100g': 2.7,
        'carbs_per_100g': 28,
        'fats_per_100g': 0.3,
        'fiber_per_100g': 0.4,
        'serving_size': 100,
    },
    'Roti/Chapati': {
        'calories_per_100g': 297,
        'protein_per_100g': 11,
        'carbs_per_100g': 58,
        'fats_per_100g': 2,
        'fiber_per_100g': 2.7,
        'serving_size': 50,  # 1 roti
    },
    'Vegetable Curry': {
        'calories_per_100g': 80,
        'protein_per_100g': 2,
        'carbs_per_100g': 12,
        'fats_per_100g': 3,
        'fiber_per_100g': 4,
        'serving_size': 150,
    },
    'Chicken Curry': {
        'calories_per_100g': 200,
        'protein_per_100g': 20,
        'carbs_per_100g': 5,
        'fats_per_100g': 10,
        'fiber_per_100g': 0.5,
        'serving_size': 150,
    },
    'Fish Curry': {
        'calories_per_100g': 150,
        'protein_per_100g': 18,
        'carbs_per_100g': 4,
        'fats_per_100g': 6,
        'fiber_per_100g': 0.3,
        'serving_size': 150,
    },
    'Paneer Curry': {
        'calories_per_100g': 250,
        'protein_per_100g': 18,
        'carbs_per_100g': 8,
        'fats_per_100g': 18,
        'fiber_per_100g': 0.5,
        'serving_size': 150,
    },
    'Sambar': {
        'calories_per_100g': 90,
        'protein_per_100g': 4,
        'carbs_per_100g': 15,
        'fats_per_100g': 2,
        'fiber_per_100g': 5,
        'serving_size': 150,
    },
    'Rasam': {
        'calories_per_100g': 30,
        'protein_per_100g': 1,
        'carbs_per_100g': 6,
        'fats_per_100g': 0.5,
        'fiber_per_100g': 1,
        'serving_size': 150,
    },
    
    # Snacks
    'Fruits (Mixed)': {
        'calories_per_100g': 60,
        'protein_per_100g': 0.8,
        'carbs_per_100g': 15,
        'fats_per_100g': 0.2,
        'fiber_per_100g': 2.5,
        'serving_size': 100,
    },
    'Nuts (Mixed)': {
        'calories_per_100g': 600,
        'protein_per_100g': 15,
        'carbs_per_100g': 20,
        'fats_per_100g': 50,
        'fiber_per_100g': 8,
        'serving_size': 30,  # 1 handful
    },
    'Yogurt/Curd': {
        'calories_per_100g': 60,
        'protein_per_100g': 3.5,
        'carbs_per_100g': 4.5,
        'fats_per_100g': 3.5,
        'fiber_per_100g': 0,
        'serving_size': 100,
    },
    'Tea': {
        'calories_per_100g': 2,
        'protein_per_100g': 0,
        'carbs_per_100g': 0.3,
        'fats_per_100g': 0,
        'fiber_per_100g': 0,
        'serving_size': 200,  # 1 cup
    },
    'Coffee': {
        'calories_per_100g': 2,
        'protein_per_100g': 0.1,
        'carbs_per_100g': 0,
        'fats_per_100g': 0,
        'fiber_per_100g': 0,
        'serving_size': 200,
    },
    
    # Western Foods
    'Oatmeal': {
        'calories_per_100g': 389,
        'protein_per_100g': 17,
        'carbs_per_100g': 66,
        'fats_per_100g': 7,
        'fiber_per_100g': 11,
        'serving_size': 100,
    },
    'Eggs (Scrambled)': {
        'calories_per_100g': 149,
        'protein_per_100g': 10,
        'carbs_per_100g': 1.5,
        'fats_per_100g': 11,
        'fiber_per_100g': 0,
        'serving_size': 100,  # 2 eggs
    },
    'Bread (White)': {
        'calories_per_100g': 265,
        'protein_per_100g': 9,
        'carbs_per_100g': 49,
        'fats_per_100g': 3.2,
        'fiber_per_100g': 2.7,
        'serving_size': 30,  # 1 slice
    },
    'Salad': {
        'calories_per_100g': 25,
        'protein_per_100g': 1,
        'carbs_per_100g': 5,
        'fats_per_100g': 0.2,
        'fiber_per_100g': 2,
        'serving_size': 100,
    },
    'Chicken Breast (Grilled)': {
        'calories_per_100g': 165,
        'protein_per_100g': 31,
        'carbs_per_100g': 0,
        'fats_per_100g': 3.6,
        'fiber_per_100g': 0,
        'serving_size': 150,
    },
    'Salmon (Grilled)': {
        'calories_per_100g': 206,
        'protein_per_100g': 22,
        'carbs_per_100g': 0,
        'fats_per_100g': 12,
        'fiber_per_100g': 0,
        'serving_size': 150,
    },
    'Quinoa (Cooked)': {
        'calories_per_100g': 120,
        'protein_per_100g': 4.4,
        'carbs_per_100g': 22,
        'fats_per_100g': 1.9,
        'fiber_per_100g': 2.8,
        'serving_size': 100,
    },
    'Banana': {
        'calories_per_100g': 89,
        'protein_per_100g': 1.1,
        'carbs_per_100g': 23,
        'fats_per_100g': 0.3,
        'fiber_per_100g': 2.6,
        'serving_size': 100,  # 1 medium banana
    },
    'Apple': {
        'calories_per_100g': 52,
        'protein_per_100g': 0.3,
        'carbs_per_100g': 14,
        'fats_per_100g': 0.2,
        'fiber_per_100g': 2.4,
        'serving_size': 150,  # 1 medium apple
    },
    'Milk': {
        'calories_per_100g': 42,
        'protein_per_100g': 3.4,
        'carbs_per_100g': 5,
        'fats_per_100g': 1,
        'fiber_per_100g': 0,
        'serving_size': 200,  # 1 glass
    },
}


def get_food_info(food_name):
    """Get nutritional information for a food item"""
    return FOOD_DATABASE.get(food_name, None)


def calculate_nutrition(food_name, quantity, unit='serving'):
    """Calculate nutrition for given quantity of food"""
    food_info = get_food_info(food_name)
    if not food_info:
        return None
    
    # Convert quantity to grams if needed
    if unit == 'serving' or unit == 'servings':
        # If serving, multiply by serving_size to get grams
        quantity_grams = quantity * food_info['serving_size']
    elif unit == 'gram' or unit == 'g' or unit == 'grams':
        quantity_grams = quantity
    else:
        # Default to serving
        quantity_grams = quantity * food_info['serving_size']
    
    # Calculate per 100g basis
    multiplier = quantity_grams / 100.0
    
    return {
        'calories': round(food_info['calories_per_100g'] * multiplier, 2),
        'protein': round(food_info['protein_per_100g'] * multiplier, 2),
        'carbs': round(food_info['carbs_per_100g'] * multiplier, 2),
        'fats': round(food_info['fats_per_100g'] * multiplier, 2),
        'fiber': round(food_info['fiber_per_100g'] * multiplier, 2),
    }


def get_food_suggestions(meal_type, dietary_preference='none'):
    """Get food suggestions based on meal type and dietary preference"""
    suggestions = {
        'breakfast': ['Poha (Flattened Rice)', 'Upma (Semolina)', 'Idli', 'Dosa', 'Paratha', 'Aloo Paratha', 'Besan Chilla', 'Moong Dal Cheela', 'Oatmeal', 'Eggs (Scrambled)', 'Bread (White)'],
        'lunch': ['Rice (Cooked)', 'Roti/Chapati', 'Dal (Lentils)', 'Vegetable Curry', 'Chicken Curry', 'Fish Curry', 'Paneer Curry', 'Sambar', 'Rasam', 'Salad', 'Quinoa (Cooked)'],
        'dinner': ['Rice (Cooked)', 'Roti/Chapati', 'Dal (Lentils)', 'Vegetable Curry', 'Chicken Curry', 'Fish Curry', 'Paneer Curry', 'Chicken Breast (Grilled)', 'Salmon (Grilled)', 'Quinoa (Cooked)'],
        'snacks': ['Fruits (Mixed)', 'Nuts (Mixed)', 'Yogurt/Curd', 'Banana', 'Apple', 'Tea', 'Coffee'],
    }
    
    foods = suggestions.get(meal_type, [])
    
    # Filter based on dietary preference
    if dietary_preference == 'vegetarian':
        foods = [f for f in foods if 'Chicken' not in f and 'Fish' not in f and 'Salmon' not in f and 'Eggs' not in f]
    elif dietary_preference == 'vegan':
        foods = [f for f in foods if 'Chicken' not in f and 'Fish' not in f and 'Salmon' not in f and 'Eggs' not in f and 'Milk' not in f and 'Yogurt' not in f and 'Paneer' not in f]
    
    return foods

