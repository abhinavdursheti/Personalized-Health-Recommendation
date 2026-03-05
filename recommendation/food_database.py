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
        # Approx. 100 kcal per serving
        'calories_per_100g': 100,
        'protein_per_100g': 4,
        'carbs_per_100g': 18,
        'fats_per_100g': 3,
        'fiber_per_100g': 4,
        'serving_size': 100,
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
        # Approx. 40 kcal per cup
        'calories_per_100g': 20,
        'protein_per_100g': 1,
        'carbs_per_100g': 8,
        'fats_per_100g': 0.5,
        'fiber_per_100g': 0,
        'serving_size': 200,  # 1 cup
    },
    'Coffee': {
        # Approx. 30 kcal per cup
        'calories_per_100g': 15,
        'protein_per_100g': 1,
        'carbs_per_100g': 5,
        'fats_per_100g': 0.5,
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

    # Additional Indian breakfast accompaniments
    'Peanut Chutney': {
        # ~120 kcal per serving
        'calories_per_100g': 120,
        'protein_per_100g': 5,
        'carbs_per_100g': 6,
        'fats_per_100g': 9,
        'fiber_per_100g': 2,
        'serving_size': 100,
    },
    'Tomato Chutney': {
        # ~80 kcal per serving
        'calories_per_100g': 80,
        'protein_per_100g': 2,
        'carbs_per_100g': 12,
        'fats_per_100g': 3,
        'fiber_per_100g': 2,
        'serving_size': 100,
    },
    'Bonda': {
        # ~180 kcal per piece/serving
        'calories_per_100g': 180,
        'protein_per_100g': 5,
        'carbs_per_100g': 20,
        'fats_per_100g': 8,
        'fiber_per_100g': 2,
        'serving_size': 100,
    },
    'Vada': {
        # ~160 kcal per piece/serving
        'calories_per_100g': 160,
        'protein_per_100g': 5,
        'carbs_per_100g': 18,
        'fats_per_100g': 6,
        'fiber_per_100g': 3,
        'serving_size': 100,
    },

    # Additional Indian lunch/dinner dishes
    'Chicken Biryani': {
        # ~290 kcal per serving
        'calories_per_100g': 290,
        'protein_per_100g': 13,
        'carbs_per_100g': 28,
        'fats_per_100g': 12,
        'fiber_per_100g': 2,
        'serving_size': 100,
    },
    'Mutton Biryani': {
        # ~350 kcal per serving
        'calories_per_100g': 350,
        'protein_per_100g': 15,
        'carbs_per_100g': 30,
        'fats_per_100g': 16,
        'fiber_per_100g': 2,
        'serving_size': 100,
    },
    'Mutton Curry': {
        # ~320 kcal per serving
        'calories_per_100g': 320,
        'protein_per_100g': 18,
        'carbs_per_100g': 6,
        'fats_per_100g': 24,
        'fiber_per_100g': 1,
        'serving_size': 100,
    },
    'Tandoori Chicken': {
        # ~220 kcal per serving
        'calories_per_100g': 220,
        'protein_per_100g': 26,
        'carbs_per_100g': 2,
        'fats_per_100g': 12,
        'fiber_per_100g': 0,
        'serving_size': 100,
    },
    'Butter Naan': {
        # ~260 kcal per naan
        'calories_per_100g': 260,
        'protein_per_100g': 8,
        'carbs_per_100g': 40,
        'fats_per_100g': 8,
        'fiber_per_100g': 2,
        'serving_size': 100,
    },
    'Brinjal Curry': {
        # ~150 kcal per serving
        'calories_per_100g': 150,
        'protein_per_100g': 4,
        'carbs_per_100g': 12,
        'fats_per_100g': 9,
        'fiber_per_100g': 4,
        'serving_size': 100,
    },
    'Egg Curry': {
        # ~200 kcal per serving
        'calories_per_100g': 200,
        'protein_per_100g': 12,
        'carbs_per_100g': 6,
        'fats_per_100g': 14,
        'fiber_per_100g': 0,
        'serving_size': 100,
    },
    'Egg Fried Rice': {
        # ~250 kcal per serving
        'calories_per_100g': 250,
        'protein_per_100g': 7,
        'carbs_per_100g': 32,
        'fats_per_100g': 9,
        'fiber_per_100g': 1,
        'serving_size': 100,
    },

    # Additional snacks
    'Maggi': {
        # ~310 kcal per packet/serving
        'calories_per_100g': 310,
        'protein_per_100g': 7,
        'carbs_per_100g': 45,
        'fats_per_100g': 11,
        'fiber_per_100g': 2,
        'serving_size': 100,
    },
    'Bread Omelette': {
        # ~250 kcal per serving
        'calories_per_100g': 250,
        'protein_per_100g': 12,
        'carbs_per_100g': 20,
        'fats_per_100g': 13,
        'fiber_per_100g': 2,
        'serving_size': 100,
    },
    'French Fries': {
        # ~365 kcal per serving
        'calories_per_100g': 365,
        'protein_per_100g': 4,
        'carbs_per_100g': 40,
        'fats_per_100g': 17,
        'fiber_per_100g': 3,
        'serving_size': 100,
    },
    'Momos': {
        # ~180 kcal per serving
        'calories_per_100g': 180,
        'protein_per_100g': 7,
        'carbs_per_100g': 24,
        'fats_per_100g': 6,
        'fiber_per_100g': 1,
        'serving_size': 100,
    },
    'Chaat': {
        # ~220 kcal per serving
        'calories_per_100g': 220,
        'protein_per_100g': 6,
        'carbs_per_100g': 28,
        'fats_per_100g': 9,
        'fiber_per_100g': 4,
        'serving_size': 100,
    },
    'Samosa': {
        # ~260 kcal per piece/serving
        'calories_per_100g': 260,
        'protein_per_100g': 5,
        'carbs_per_100g': 28,
        'fats_per_100g': 13,
        'fiber_per_100g': 3,
        'serving_size': 100,
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
        'breakfast': [
            'Poha (Flattened Rice)', 'Upma (Semolina)', 'Idli', 'Dosa', 'Paratha', 'Aloo Paratha',
            'Besan Chilla', 'Moong Dal Cheela', 'Oatmeal', 'Eggs (Scrambled)', 'Bread (White)',
            'Peanut Chutney', 'Tomato Chutney', 'Sambar', 'Bonda', 'Vada',
        ],
        'lunch': [
            'Rice (Cooked)', 'Roti/Chapati', 'Dal (Lentils)', 'Vegetable Curry',
            'Chicken Curry', 'Fish Curry', 'Paneer Curry', 'Sambar', 'Rasam',
            'Salad', 'Quinoa (Cooked)',
            'Chicken Biryani', 'Mutton Biryani', 'Mutton Curry', 'Tandoori Chicken',
            'Butter Naan', 'Brinjal Curry', 'Egg Curry', 'Egg Fried Rice',
        ],
        'dinner': [
            'Rice (Cooked)', 'Roti/Chapati', 'Dal (Lentils)', 'Vegetable Curry',
            'Chicken Curry', 'Fish Curry', 'Paneer Curry', 'Chicken Breast (Grilled)',
            'Salmon (Grilled)', 'Quinoa (Cooked)',
            'Chicken Biryani', 'Mutton Biryani', 'Mutton Curry', 'Tandoori Chicken',
            'Butter Naan', 'Brinjal Curry', 'Egg Curry', 'Egg Fried Rice',
        ],
        'snacks': [
            'Fruits (Mixed)', 'Nuts (Mixed)', 'Yogurt/Curd', 'Banana', 'Apple',
            'Tea', 'Coffee', 'Maggi', 'Bread Omelette', 'French Fries',
            'Momos', 'Chaat', 'Samosa',
        ],
    }
    
    foods = suggestions.get(meal_type, [])
    
    # Filter based on dietary preference
    if dietary_preference == 'vegetarian':
        foods = [f for f in foods if 'Chicken' not in f and 'Fish' not in f and 'Salmon' not in f and 'Eggs' not in f]
    elif dietary_preference == 'vegan':
        foods = [f for f in foods if 'Chicken' not in f and 'Fish' not in f and 'Salmon' not in f and 'Eggs' not in f and 'Milk' not in f and 'Yogurt' not in f and 'Paneer' not in f]
    
    return foods


# Food Replacement Engine: map keywords/phrases to healthier alternatives
# Keys are lowercased; we match if user input contains the key
FOOD_REPLACEMENT_MAP = {
    # Biryani / rice dishes
    'biryani': [
        'Brown rice pulao with vegetables',
        'Grilled chicken + roti + dal',
        'Millet bowl (foxtail or barnyard) with curry',
        'Quinoa (Cooked) with Chicken Curry or Vegetable Curry',
    ],
    'chicken biryani': [
        'Brown rice pulao with grilled chicken',
        'Grilled chicken + roti + dal',
        'Millet bowl with chicken curry',
    ],
    'mutton biryani': [
        'Brown rice pulao with lean meat',
        'Grilled chicken + roti',
        'Millet bowl with dal',
    ],
    'fried rice': [
        'Rice (Cooked) with Vegetable Curry (no extra oil)',
        'Quinoa (Cooked) with stir-fried vegetables',
        'Brown rice pulao',
    ],
    'pulao': [
        'Brown rice pulao',
        'Quinoa (Cooked) with vegetables',
        'Millet bowl',
    ],
    # Fried / heavy items
    'paratha': [
        'Roti/Chapati (whole wheat)',
        'Besan Chilla',
        'Moong Dal Cheela',
    ],
    'aloo paratha': [
        'Roti/Chapati with Dal (Lentils)',
        'Besan Chilla',
        'Moong Dal Cheela',
    ],
    'samosa': [
        'Baked vegetable cutlet',
        'Moong Dal Cheela',
        'Fruits (Mixed) or Nuts (Mixed)',
    ],
    'pakora': [
        'Besan Chilla',
        'Steamed vegetables with Yogurt/Curd',
        'Nuts (Mixed)',
    ],
    'bhatura': [
        'Roti/Chapati',
        'Idli',
        'Dosa (with less oil)',
    ],
    'naan': [
        'Roti/Chapati',
        'Whole wheat phulka',
    ],
    # Sweets / desserts
    'gulab jamun': [
        'Fruits (Mixed)',
        'Yogurt/Curd with honey',
        'Apple or Banana',
    ],
    'jalebi': [
        'Fruits (Mixed)',
        'Oatmeal with banana',
    ],
    'kheer': [
        'Yogurt/Curd',
        'Fruits (Mixed)',
        'Oatmeal with milk and nuts',
    ],
    'brownie': [
        'Yogurt/Curd with a small piece of dark chocolate',
        'Fruits (Mixed) with nuts',
        'Oatmeal with cocoa (less sugar)',
    ],
    'cake': [
        'Fruits (Mixed)',
        'Yogurt/Curd with fruits',
        'Small portion of dark chocolate with nuts',
    ],
    'dessert': [
        'Fruits (Mixed)',
        'Yogurt/Curd with a little honey',
        'Banana with nuts',
    ],
    # General
    'white rice': [
        'Rice (Cooked) in smaller portion + more vegetables',
        'Quinoa (Cooked)',
        'Brown rice pulao',
    ],
    'rice': [
        'Quinoa (Cooked)',
        'Brown rice pulao',
        'Millet bowl',
    ],
    'curry': [
        'Vegetable Curry or Chicken Curry with less oil',
        'Dal (Lentils)',
        'Salad with grilled protein',
    ],
    'pizza': [
        'Roti/Chapati with Vegetable Curry',
        'Salad with Chicken Breast (Grilled)',
        'Besan Chilla with vegetables',
    ],
    'burger': [
        'Grilled chicken + Salad',
        'Roti/Chapati wrap with vegetables',
        'Chicken Breast (Grilled) with Salad',
    ],
    'pasta': [
        'Quinoa (Cooked) with vegetables',
        'Dal (Lentils) with Roti/Chapati',
        'Vegetable Curry with Rice (Cooked)',
    ],
    'bread': [
        'Roti/Chapati',
        'Oatmeal',
        'Idli or Dosa',
    ],
    'dosa': [
        'Idli (steamed)',
        'Moong Dal Cheela',
        'Besan Chilla',
    ],
    # Sugary drinks / sodas
    'pepsi': [
        'Diet soda (occasionally, smaller portion)',
        'Sparkling water with lemon',
        'Unsweetened iced tea',
    ],
    'coke': [
        'Diet soda (occasionally, smaller portion)',
        'Sparkling water with lemon',
        'Unsweetened iced tea',
    ],
    'cola': [
        'Diet soda (occasionally, smaller portion)',
        'Sparkling water with lemon',
        'Unsweetened iced tea',
    ],
    'soft drink': [
        'Sparkling water with lemon or lime',
        'Unsweetened iced tea',
        'Plain water plus a small fruit snack',
    ],
    'soda': [
        'Sparkling water with lemon',
        'Diet soda (occasionally)',
        'Unsweetened iced tea',
    ],
}


def get_food_replacements(food_query):
    """
    Suggest healthier alternatives for a given food.
    Returns list of dicts: [{'name': '...', 'in_database': bool}, ...]
    """
    if not food_query or not food_query.strip():
        return []
    query = food_query.strip().lower()
    alternatives = []
    seen = set()
    # Sort keys by length descending so longer matches (e.g. 'chicken biryani') win
    for key in sorted(FOOD_REPLACEMENT_MAP.keys(), key=len, reverse=True):
        if key in query or query in key:
            for alt in FOOD_REPLACEMENT_MAP[key]:
                alt_clean = alt.strip()
                if alt_clean not in seen:
                    seen.add(alt_clean)
                    alternatives.append({
                        'name': alt_clean,
                        'in_database': alt_clean in FOOD_DATABASE,
                    })
            break  # Use first matching group only to avoid duplicates
    # If no match, suggest generic healthier habits
    if not alternatives:
        alternatives = [
            {'name': 'Add more vegetables and lean protein', 'in_database': False},
            {'name': 'Choose grilled or steamed over fried', 'in_database': False},
            {'name': 'Try smaller portion with Salad or Dal (Lentils)', 'in_database': False},
        ]
    return alternatives

