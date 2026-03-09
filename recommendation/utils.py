"""
Utility functions for recommendation system
"""
import statistics
import json

from .ml_models.diet_model import DietRecommendationModel


def calculate_recovery_score(health_data, profile):
    """
    Single-day Health Recovery Score (0-100). Uses same bands as 7-day so poor
    habits (low sleep, low exercise, calorie imbalance) produce lower scores.
    Returns dict: { 'score': int 0-100, 'label': str }
    """
    if health_data is None:
        return {'score': None, 'label': 'No data'}

    # Sleep (max 30): ≥7→30, 6-7→20, 5-6→10, <5→5
    sleep_hours = health_data.sleep_hours
    if sleep_hours is None:
        sleep_score = 5
    elif sleep_hours >= 7:
        sleep_score = 30
    elif sleep_hours >= 6:
        sleep_score = 20
    elif sleep_hours >= 5:
        sleep_score = 10
    else:
        sleep_score = 5

    # Activity (max 25): treat single day as proxy for weekly (30 min ≈ 150/week)
    exercise_minutes = health_data.exercise_minutes or 0
    if exercise_minutes >= 30:
        activity_score = 25
    elif exercise_minutes >= 20:
        activity_score = 18
    elif exercise_minutes >= 10:
        activity_score = 12
    else:
        activity_score = 5

    # Calories vs TDEE (max 25): within ±200→25, 200-400 diff→15, >400→5
    tdee = getattr(profile, 'tdee', None) or 2000
    calories = health_data.total_calories or health_data.calories_consumed
    if calories is None:
        calorie_score = 5
    else:
        diff = abs(calories - tdee)
        if diff <= 200:
            calorie_score = 25
        elif diff <= 400:
            calorie_score = 15
        else:
            calorie_score = 5

    # Stress Level (max 20): 1-3→20, 4-6→12, 7-8→6, 9-10→0
    stress_level = health_data.stress_level
    if stress_level is None:
        stress_score = 10
    elif stress_level <= 3:
        stress_score = 20
    elif stress_level <= 6:
        stress_score = 12
    elif stress_level <= 8:
        stress_score = 6
    else:
        stress_score = 0

    total = sleep_score + activity_score + calorie_score + stress_score
    score = min(100, max(0, total))

    if score >= 80:
        label = 'Excellent'
    elif score >= 60:
        label = 'Good'
    elif score >= 40:
        label = 'Moderate'
    else:
        label = 'Poor'

    return {'score': int(round(score)), 'label': label}


def compute_recovery_score_7day(profile, health_data_list):
    """
    Health Recovery Score from last 7 days of HealthData (0-100).
    Sleep (30) + Exercise (25) + Calorie balance (25) + Weight trend (20).
    Recalculates whenever new data is logged.
    Returns: { 'score': int 0-100, 'label': str, 'components': dict }
    """
    if not health_data_list:
        return {'score': 0, 'label': 'Poor', 'components': {}}
    data = sorted(health_data_list, key=lambda d: d.date)
    window = data[-7:]  # most recent 7 records
    tdee = getattr(profile, 'tdee', None) or 2000

    def avg(lst, default=0):
        return statistics.mean(lst) if lst else default

    sleep_vals = [d.sleep_hours for d in window if d.sleep_hours is not None]
    exercise_vals = [d.exercise_minutes for d in window if d.exercise_minutes is not None]
    calorie_vals = [
        (d.calories_consumed if d.calories_consumed is not None else d.total_calories)
        for d in window if (d.calories_consumed is not None) or d.total_calories
    ]
    weight_vals = [d.weight for d in window if d.weight is not None]

    average_sleep_hours = avg(sleep_vals, default=0)
    total_weekly_exercise_minutes = sum(exercise_vals) if exercise_vals else 0
    average_calories = avg(calorie_vals, default=tdee)
    # Weight trend: change over the 7-day window (kg)
    if len(weight_vals) >= 2:
        weight_trend_7d = weight_vals[-1] - weight_vals[0]
    else:
        weight_trend_7d = 0

    # Sleep Score (max 30)
    if average_sleep_hours >= 7:
        sleep_score = 30
    elif average_sleep_hours >= 6:
        sleep_score = 20
    elif average_sleep_hours >= 5:
        sleep_score = 10
    else:
        sleep_score = 5

    # Exercise Score (max 25): total weekly minutes
    if total_weekly_exercise_minutes >= 150:
        exercise_score = 25
    elif total_weekly_exercise_minutes >= 90:
        exercise_score = 18
    elif total_weekly_exercise_minutes >= 60:
        exercise_score = 12
    else:
        exercise_score = 5

    # Calorie Balance Score (max 25): difference from TDEE
    diff = abs(average_calories - tdee)
    if diff <= 200:
        calorie_score = 25
    elif diff <= 400:
        calorie_score = 15
    else:
        calorie_score = 5

    # Weight Trend Score (max 20): stable/decrease → 20, +1–2 kg → 12, >2 kg → 5
    if weight_trend_7d <= 0:
        weight_score = 20
    elif weight_trend_7d <= 2:
        weight_score = 12
    else:
        weight_score = 5

    total = sleep_score + exercise_score + calorie_score + weight_score
    score = min(100, max(0, total))

    if score >= 80:
        label = 'Excellent'
    elif score >= 60:
        label = 'Good'
    elif score >= 40:
        label = 'Moderate'
    else:
        label = 'Poor'

    return {
        'score': int(round(score)),
        'label': label,
        'components': {
            'sleep_score': sleep_score,
            'exercise_score': exercise_score,
            'calorie_score': calorie_score,
            'weight_score': weight_score,
            'average_sleep_hours': round(average_sleep_hours, 1),
            'total_weekly_exercise_minutes': int(total_weekly_exercise_minutes),
            'average_calories_vs_tdee': round(average_calories - tdee, 0),
            'weight_trend_last_7_days': round(weight_trend_7d, 2),
        },
    }
from .ml_models.exercise_model import ExerciseRecommendationModel
from .ml_models.sleep_model import SleepRecommendationModel
from .ml_models.recovery_stability_model import RecoveryStabilityModel
from .ml_models.habit_sensitivity_model import HabitSensitivityModel
from .ml_models.disease_prediction_model import DiseasePredictionModel
from .ml_models.simulator_model import HealthSimulatorModel


def generate_diet_recommendation(user_profile):
    """Generate diet recommendation for user"""
    model = DietRecommendationModel()
    
    # Calculate calories based on TDEE (Total Daily Energy Expenditure)
    # TDEE is already calculated correctly using Mifflin-St Jeor equation
    base_calories = user_profile.tdee
    
    # Adjust based on health goal
    if user_profile.health_goal == 'weight_loss':
        # 15-20% deficit for weight loss (500-700 calories deficit)
        calories = base_calories - 500
    elif user_profile.health_goal == 'muscle_gain':
        # 10-15% surplus for muscle gain (300-500 calories surplus)
        calories = base_calories + 400
    else:  # maintenance or general
        # Use TDEE as is for maintenance
        calories = base_calories
    
    # Ensure minimum calories for health (1200 for women, 1500 for men)
    min_calories = 1200 if user_profile.gender == 'F' else 1500
    calories = max(min_calories, round(calories, 0))
    
    # Get macronutrients
    macros = model.get_macronutrients(calories, user_profile.health_goal)
    
    # Generate meal plan
    allergies_list = [a.strip() for a in user_profile.allergies.split(',')] if user_profile.allergies else []
    meal_plan = model.generate_meal_plan(calories, user_profile.dietary_preference, allergies_list)
    
    return {
        'calories': calories,
        'macronutrients': macros,
        'meal_plan': meal_plan,
        'tdee': user_profile.tdee,
        'bmr': user_profile.bmr,
    }


def generate_exercise_recommendation(user_profile):
    """Generate exercise recommendation for user"""
    model = ExerciseRecommendationModel()
    
    fitness_level = model.get_fitness_level(
        user_profile.activity_level,
        user_profile.age,
        user_profile.bmi
    )
    
    # Default available time based on activity level
    time_map = {
        'sedentary': 30,
        'light': 45,
        'moderate': 60,
        'active': 75,
        'very_active': 90,
    }
    available_time = time_map.get(user_profile.activity_level, 45)
    
    recommendation = model.recommend_exercises(
        fitness_level,
        user_profile.health_goal,
        available_time,
        user_profile.age,
        user_profile.bmi
    )
    
    return recommendation


def generate_sleep_recommendation(user_profile, exercise_minutes=0):
    """Generate sleep recommendation for user"""
    model = SleepRecommendationModel()
    
    sleep_hours = model.predict_sleep_hours(
        user_profile.age,
        user_profile.activity_level,
        user_profile.bmi,
        exercise_minutes
    )
    
    sleep_schedule = model.get_sleep_schedule(sleep_hours)
    sleep_tips = model.get_sleep_tips(user_profile.age, user_profile.activity_level)
    
    return {
        'sleep_hours': sleep_hours,
        'schedule': sleep_schedule,
        'tips': sleep_tips,
    }


def generate_recovery_stability_analysis(user_profile, health_data_list):
    """
    Generate recovery and stability analysis from the most recent 7 HealthData records.
    Recalculates dynamically each time the user clicks "Generate Analysis".

    Metrics: sleep_variation, exercise_consistency, calorie_balance_vs_TDEE, weight_trend.
    Recovery score: Sleep (30) + Exercise (25) + Calorie (25) + Weight trend (20) = 0–100.
    Risk from centralized calculate_health_risk().
    """
    from datetime import timedelta

    def _avg_local(values):
        return statistics.mean(values) if values else 0.0

    if not health_data_list:
        return {
            'recovery_days': 5,
            'stability_score': 0,
            'is_stable': False,
            'risk_level': 'High',
            'consistency_score': 0,
            'adherence_rate': 0,
            'streak_days': 0,
            'missed_days': 0,
            'recommendations': [
                "Start logging your sleep, activity, and meals for at least a week.",
                "Short daily walks and a consistent bedtime will immediately improve recovery."
            ],
            'metrics': {},
        }

    # Most recent 7 HealthData records (dynamic each time)
    data = sorted(health_data_list, key=lambda d: d.date)
    window = data[-7:] if len(data) >= 7 else data
    end_date = window[-1].date
    window_start_d = window[0].date
    expected_days = (end_date - window_start_d).days + 1
    unique_dates_in_window = {d.date for d in window}
    days_logged = len(unique_dates_in_window)

    sleep_values = [d.sleep_hours for d in window if d.sleep_hours is not None]
    exercise_values = [d.exercise_minutes for d in window if d.exercise_minutes is not None]
    calorie_values = [
        (d.calories_consumed if d.calories_consumed is not None else d.total_calories)
        for d in window
        if (d.calories_consumed is not None) or d.total_calories
    ]
    weight_values = [d.weight for d in window if d.weight is not None]

    avg_sleep = _avg_local(sleep_values)
    avg_exercise = _avg_local(exercise_values)
    avg_calories = _avg_local(calorie_values)
    tdee = getattr(user_profile, 'tdee', None) or 2000

    # --- Metrics recalculated each run ---
    sleep_variation = round(_safe_std(sleep_values), 2) if len(sleep_values) >= 2 else 0
    calorie_variation = round(_safe_std(calorie_values), 0) if len(calorie_values) >= 2 else 0
    weight_trend = 0
    if len(weight_values) >= 2:
        weight_trend = round(weight_values[-1] - weight_values[0], 2)
    days_with_exercise = sum(1 for d in window if (d.exercise_minutes or 0) >= 15)
    exercise_consistency = round((days_with_exercise / len(window)) * 100, 0) if window else 0
    calorie_balance_vs_TDEE = round((avg_calories or tdee) - tdee, 0) if tdee else 0

    # --- Current streak ---
    unique_dates = sorted({d.date for d in window}, reverse=True)
    streak_days = 0
    if unique_dates:
        streak_days = 1
        prev = unique_dates[0]
        for dt in unique_dates[1:]:
            if (prev - dt).days == 1:
                streak_days += 1
                prev = dt
            else:
                break

    # --- Consistency score (days_logged / expected_days * 100) ---
    total_span_days = expected_days
    missed_days = max(0, expected_days - days_logged)
    consistency_score = round((days_logged / expected_days) * 100, 1) if expected_days else 0
    adherence_rate = round(days_logged / expected_days, 2) if expected_days else 0

    # --- Recovery score from 7-day formula (Sleep 30 + Exercise 25 + Calorie 25 + Weight 20) ---
    recovery_7d = compute_recovery_score_7day(user_profile, window)
    stability_score = recovery_7d['score']

    # --- Recovery days (1–14) from sleep/calorie factors ---
    if avg_sleep <= 0:
        sleep_factor = 0.6
    elif 7 <= avg_sleep <= 8:
        sleep_factor = 1.0
    elif 6 <= avg_sleep < 7 or 8 < avg_sleep <= 9:
        sleep_factor = 0.85
    else:
        sleep_factor = 0.5
    if tdee and avg_calories:
        ratio = avg_calories / tdee
        cal_factor = 1.0 if 0.9 <= ratio <= 1.1 else (0.85 if 0.8 <= ratio <= 1.2 else 0.6)
    else:
        cal_factor = 0.7
    fatigue_factor = 1.2 if (avg_exercise or 0) > 45 else (1.0 if (avg_exercise or 0) > 20 else 0.8)
    raw_recovery_days = 5.0 * fatigue_factor / max(0.4, sleep_factor * 0.6 + cal_factor * 0.4)
    recovery_days = max(1.0, min(14.0, round(raw_recovery_days, 1)))

    # --- Risk level from centralized function (same as Overview) ---
    risk_result = calculate_health_risk(user_profile, window)
    risk_level = risk_result['risk_level']
    if risk_level == 'Moderate':
        risk_level = 'Medium'

    is_stable = stability_score >= 50

    # --- Recommendations ---
    recommendations = []
    if avg_sleep and avg_sleep < 6:
        recommendations.append("Improve sleep duration for better recovery (aim for 7–8 hours).")
    if (avg_exercise or 0) < 20:
        recommendations.append("Increase physical activity (target at least 20–30 minutes most days).")
    if tdee and avg_calories:
        r = avg_calories / tdee
        if r < 0.8:
            recommendations.append("Your calorie deficit is high; balance intake to support recovery.")
        elif r > 1.2:
            recommendations.append("Calorie intake is above needs; reduce surplus for long-term health.")
    if consistency_score < 75:
        recommendations.append("Log most days each week to improve consistency.")
    if not recommendations:
        recommendations.append("Recovery and stability look solid. Maintain your routine and track progress.")

    metrics = {
        'window_days': total_span_days,
        'avg_sleep': round(avg_sleep, 1) if avg_sleep else None,
        'avg_exercise_minutes': round(avg_exercise, 1) if avg_exercise else None,
        'avg_calories': round(avg_calories, 0) if avg_calories else None,
        'has_weight_data': bool(weight_values),
        'sleep_variation': sleep_variation,
        'calorie_variation': calorie_variation,
        'calorie_balance_vs_TDEE': calorie_balance_vs_TDEE,
        'weight_trend': weight_trend,
        'exercise_consistency': exercise_consistency,
    }

    return {
        'recovery_days': recovery_days,
        'stability_score': stability_score,
        'is_stable': is_stable,
        'risk_level': risk_level,
        'consistency_score': round(consistency_score, 1),
        'adherence_rate': adherence_rate,
        'streak_days': streak_days,
        'missed_days': missed_days,
        'recommendations': recommendations,
        'metrics': metrics,
    }


def generate_correlation_analysis(health_data_list, tdee=None):
    """
    Generate behavior-cause correlation analysis from user's actual health data.
    Uses last 14–30 records. Computes Pearson correlations via pandas.
    Correlates: sleep vs weight, calories vs weight, exercise vs weight,
    exercise vs sleep, exercise vs recovery_score (when tdee provided).
    Identifies strongest correlation and returns dynamic root causes and insights.
    """
    import pandas as pd
    import numpy as np

    tdee = tdee or 2000
    if not health_data_list or len(health_data_list) < 2:
        return {
            'insights': [],
            'correlations': {},
            'root_causes': ['Not enough data. Log at least 2 days to see correlations.'],
            'data_points': len(health_data_list) if health_data_list else 0,
        }

    # Use last 14–30 records, chronological order
    data = sorted(health_data_list, key=lambda d: d.date)
    n = min(30, max(14, len(data)))
    window = data[-n:]

    # Build DataFrame
    records = []
    for d in window:
        if d.weight is None:
            continue
        
        sh = d.sleep_hours if d.sleep_hours is not None else np.nan
        ex = float(d.exercise_minutes) if d.exercise_minutes is not None else np.nan
        cal = d.calories_consumed if d.calories_consumed is not None else d.total_calories
        cal = float(cal) if cal else np.nan
        
        # Daily recovery score (same weights as recovery analysis, no streak component)
        ss = min(1.0, (sh if not np.isnan(sh) else 0) / 8.0)
        ac = min(1.0, (ex if not np.isnan(ex) else 0) / 30.0)
        cb = min(1.2, (cal / tdee) if not np.isnan(cal) and tdee else 0.8)
        raw = ss * 0.4 + ac * 0.3 + cb * 0.2
        rec_score = min(100, raw * 100)

        records.append({
            'date': d.date,
            'weight': float(d.weight),
            'sleep': sh,
            'exercise': ex,
            'calories': cal,
            'recovery_score': rec_score
        })

    df = pd.DataFrame(records)
    n_valid = len(df)

    if n_valid < 2:
        return {
            'insights': [],
            'correlations': {},
            'root_causes': ['Need at least 2 days with weight data for correlation.'],
            'data_points': n_valid,
        }

    # Calculate Pearson correlations using pandas
    corr_matrix = df[['weight', 'sleep', 'exercise', 'calories', 'recovery_score']].corr(method='pearson')

    # Extract correlations safely
    def get_corr(c1, c2):
        try:
            val = corr_matrix.loc[c1, c2]
            return val if not pd.isna(val) else np.nan
        except KeyError:
            return np.nan

    corr_sleep_weight = get_corr('sleep', 'weight')
    corr_exercise_weight = get_corr('exercise', 'weight')
    corr_calories_weight = get_corr('calories', 'weight')
    corr_exercise_sleep = get_corr('exercise', 'sleep')
    corr_exercise_recovery = get_corr('exercise', 'recovery_score')

    correlations = {}
    if not np.isnan(corr_sleep_weight):
        correlations['sleep_hours_vs_weight'] = round(float(corr_sleep_weight), 3)
    if not np.isnan(corr_exercise_weight):
        correlations['exercise_minutes_vs_weight'] = round(float(corr_exercise_weight), 3)
    if not np.isnan(corr_calories_weight):
        correlations['calories_consumed_vs_weight'] = round(float(corr_calories_weight), 3)
    if not np.isnan(corr_exercise_sleep):
        correlations['exercise_minutes_vs_sleep'] = round(float(corr_exercise_sleep), 3)
    if not np.isnan(corr_exercise_recovery):
        correlations['exercise_minutes_vs_recovery_score'] = round(float(corr_exercise_recovery), 3)

    # List of (label, factor_name, value) for finding strongest
    pairs = []
    if not np.isnan(corr_sleep_weight):
        pairs.append(('Sleep vs weight', 'sleep_weight', corr_sleep_weight))
    if not np.isnan(corr_exercise_weight):
        pairs.append(('Exercise vs weight', 'exercise_weight', corr_exercise_weight))
    if not np.isnan(corr_calories_weight):
        pairs.append(('Calories vs weight', 'calories_weight', corr_calories_weight))
    if not np.isnan(corr_exercise_sleep):
        pairs.append(('Exercise vs sleep', 'exercise_sleep', corr_exercise_sleep))
    if not np.isnan(corr_exercise_recovery):
        pairs.append(('Exercise vs recovery score', 'exercise_recovery', corr_exercise_recovery))

    # Strongest by absolute value
    if not pairs:
        strongest_value = 0.0
    else:
        strongest = max(pairs, key=lambda x: abs(x[2]))
        strongest_label, strongest_key, strongest_value = strongest

    # Helper for interpreting strength
    def get_strength(c):
        abs_c = abs(c)
        if abs_c >= 0.7: return "Strong"
        if abs_c >= 0.4: return "Moderate"
        return "Weak"

    # Build insights list (one per correlation) for template
    insights = []
    root_causes = []

    def add_insight(behavior, correlation_value, insight_text, recommendation, impact='Neutral'):
        insights.append({
            'behavior': behavior,
            'correlation': round(correlation_value, 2),
            'insight': insight_text,
            'recommendation': recommendation,
            'impact': impact,
            'strength': get_strength(correlation_value)
        })

    # Sleep vs weight
    if not np.isnan(corr_sleep_weight):
        c = float(corr_sleep_weight)
        if c < -0.4:
            add_insight('Sleep duration', c, 'More sleep is associated with weight reduction.', 'Aim for 7–8 hours consistently.', 'Positive')
            if c < -0.6: root_causes.append('Low sleep may be contributing to weight gain.')
        elif c > 0.4:
            add_insight('Sleep duration', c, 'Higher sleep hours in your log correlate with higher weight.', 'Focus on sleep quality and consistent timing.', 'Negative')
        else:
            add_insight('Sleep duration', c, f'Correlation between sleep and weight is {get_strength(c).lower()}.', 'Keep logging to clarify the pattern.', 'Neutral')

    # Exercise vs weight
    if not np.isnan(corr_exercise_weight):
        c = float(corr_exercise_weight)
        if c < -0.4:
            add_insight('Exercise', c, 'More exercise is associated with lower weight.', 'Maintain or increase activity.', 'Positive')
            if c < -0.6: root_causes.append('Low exercise may be contributing to weight gain.')
        elif c > 0.4:
            add_insight('Exercise', c, 'Higher exercise correlates with higher weight in your log.', 'Review other factors (e.g. diet).', 'Negative')
        else:
            add_insight('Exercise', c, f'Correlation between exercise and weight is {get_strength(c).lower()}.', 'Keep consistent activity.', 'Neutral')

    # Calories vs weight
    if not np.isnan(corr_calories_weight):
        c = float(corr_calories_weight)
        if c > 0.4:
            add_insight('Calorie intake', c, 'High calorie intake is correlated with increasing weight.', 'Consider a moderate calorie deficit or balance.', 'Negative')
            if c > 0.6: root_causes.append('High calorie intake is strongly correlated with increasing BMI.')
        elif c < -0.4:
            add_insight('Calorie intake', c, 'Lower calories correlate with weight reduction.', 'Maintain a sustainable deficit.', 'Positive')
        else:
            add_insight('Calorie intake', c, f'Correlation between calories and weight is {get_strength(c).lower()}.', 'Monitor portion sizes and consistency.', 'Neutral')

    # Exercise vs sleep
    if not np.isnan(corr_exercise_sleep):
        c = float(corr_exercise_sleep)
        if c > 0.3:
            add_insight('Exercise & Sleep', c, 'Days with more exercise tend to have longer sleep.', 'Keep exercising to support sleep.', 'Positive')
        elif c < -0.3:
            add_insight('Exercise & Sleep', c, 'More exercise correlates with less sleep in your log.', 'Consider timing of workouts or recovery.', 'Negative')

    # Exercise vs recovery score
    if not np.isnan(corr_exercise_recovery):
        c = float(corr_exercise_recovery)
        if c > 0.4:
            add_insight('Exercise vs Recovery', c, 'More exercise is improving recovery scores.', 'Keep up consistent activity to support recovery.', 'Positive')
            if c > 0.6: root_causes.append('More exercise is strongly improving recovery scores.')
        elif c < -0.4:
            add_insight('Exercise vs Recovery', c, 'Higher exercise days correlate with lower recovery in your data.', 'Check sleep and calorie balance on high-activity days.', 'Negative')
        else:
            add_insight('Exercise vs Recovery', c, f'Correlation between exercise and recovery is {get_strength(c).lower()}.', 'Balance activity with rest and nutrition.', 'Neutral')

    # If no strong correlation found, add a neutral insight and root cause
    if not root_causes:
        root_causes.append('No strong behavioral correlation detected yet. Keep logging data.')
    if not insights:
        insights.append({
            'behavior': 'General',
            'correlation': round(strongest_value, 2) if pairs else 0,
            'insight': 'No strong correlation in current data. More points may reveal links.',
            'recommendation': 'Continue logging sleep, exercise, and calories.',
            'impact': 'Neutral',
            'strength': 'None'
        })

    # Limit root causes for display
    root_causes = root_causes[:3]

    return {
        'insights': insights,
        'correlations': correlations,
        'root_causes': root_causes,
        'data_points': n_valid,
    }


def generate_habit_sensitivity_analysis(user_profile, health_data_list):
    """Generate habit sensitivity analysis"""
    model = HabitSensitivityModel()
    return model.analyze_habits(health_data_list, user_profile)


def _safe_std(values):
    """Return population standard deviation or 0 when not enough data."""
    return statistics.pstdev(values) if len(values) > 1 else 0


def calculate_consistency_score(health_data_list):
    """
    Calculate a 0–100 Health Consistency Score across sleep, exercise, diet, and logging.
    Penalizes high variation and missed days, rewards stable habits.
    """
    if not health_data_list:
        return {
            'score': 0,
            'level': 'Low',
            'summary': 'No data yet. Add a few days of logs to see your consistency.',
            'details': {},
        }

    # Ensure data is ordered by date
    data = sorted(health_data_list, key=lambda d: d.date)
    total_span_days = (data[-1].date - data[0].date).days + 1
    unique_dates = {d.date for d in data}
    missed_days = max(total_span_days - len(unique_dates), 0)
    missed_rate = missed_days / total_span_days if total_span_days else 1

    # Extract metric series
    sleep_values = [d.sleep_hours for d in data if d.sleep_hours is not None]
    exercise_values = [d.exercise_minutes for d in data if d.exercise_minutes is not None]
    calorie_values = [
        d.calories_consumed if d.calories_consumed is not None else d.total_calories
        for d in data
        if (d.calories_consumed is not None) or d.total_calories
    ]

    def _metric_score(values, desired_min=None, desired_max=None, variation_weight=0.8, missing_weight=0.2):
        """Score a single habit on 0-100 with variation and adequacy penalties."""
        if not values:
            return 50  # neutral if no data for that metric

        avg_val = statistics.mean(values)
        variation_pct = (_safe_std(values) / avg_val * 100) if avg_val else 0
        variation_penalty = min(35, variation_pct * variation_weight)

        adequacy_penalty = 0
        if desired_min is not None and avg_val < desired_min:
            adequacy_penalty += min(25, (desired_min - avg_val) / desired_min * 60)
        if desired_max is not None and avg_val > desired_max:
            adequacy_penalty += min(20, (avg_val - desired_max) / desired_max * 40)

        missing_ratio = 1 - (len(values) / total_span_days) if total_span_days else 1
        missing_penalty = missing_ratio * 100 * missing_weight

        return max(0, 100 - (variation_penalty + adequacy_penalty + missing_penalty))

    sleep_score = _metric_score(sleep_values, desired_min=7, desired_max=9)
    exercise_score = _metric_score(exercise_values, desired_min=30, variation_weight=0.7)
    diet_score = _metric_score(calorie_values, variation_weight=0.6, missing_weight=0.15)

    logging_score = max(0, 100 - missed_rate * 120)  # heavier penalty for skipped days

    # Weighted aggregate
    score = (
        sleep_score * 0.3
        + exercise_score * 0.25
        + diet_score * 0.2
        + logging_score * 0.25
    )
    score = round(score, 1)

    if score >= 75:
        level = 'High'
        summary = 'Great job keeping habits stable and logs regular.'
    elif score >= 50:
        level = 'Moderate'
        summary = 'Some habits fluctuate; focus on steady routines and fewer missed days.'
    else:
        level = 'Low'
        summary = 'Large variations or missed days detected. Start with one small habit to stabilize.'

    details = {
        'sleep_score': round(sleep_score, 1),
        'exercise_score': round(exercise_score, 1),
        'diet_score': round(diet_score, 1),
        'logging_score': round(logging_score, 1),
        'missed_days': missed_days,
        'total_span_days': total_span_days,
    }

    return {'score': score, 'level': level, 'summary': summary, 'details': details}


def _variation_pct(values):
    """Helper: coefficient of variation (std/mean * 100) or 0 if not enough data."""
    if not values:
        return 0.0
    avg_val = statistics.mean(values)
    if not avg_val:
        return 0.0
    return (_safe_std(values) / avg_val) * 100.0


def compute_stability_index(health_data_list):
    """
    Health Stability Index (0–100).

    Uses variability in:
    - Sleep duration
    - Weight
    - Calories
    - Mood proxy (from sleep & calorie swings)

    Lower stability (more volatility) -> lower score -> higher future risk.
    """
    if not health_data_list or len(health_data_list) < 2:
        return {
            'score': None,
            'label': 'Not enough data',
            'components': {},
        }

    data = sorted(health_data_list, key=lambda d: d.date)

    sleep_values = [d.sleep_hours for d in data if d.sleep_hours is not None]
    weight_values = [d.weight for d in data if d.weight is not None]
    calorie_values = [
        d.calories_consumed if d.calories_consumed is not None else d.total_calories
        for d in data
        if (d.calories_consumed is not None) or d.total_calories
    ]

    sleep_var = _variation_pct(sleep_values)
    weight_var = _variation_pct(weight_values)
    calorie_var = _variation_pct(calorie_values)

    if sleep_values and calorie_values:
        mood_var = (sleep_var + calorie_var) / 2.0
    else:
        mood_var = max(sleep_var, calorie_var)

    volatility = (
        sleep_var * 0.3 +
        weight_var * 0.3 +
        calorie_var * 0.25 +
        mood_var * 0.15
    )

    stability_score = max(0, min(100, round(100 - min(volatility, 80))))

    if stability_score >= 75:
        label = 'Stable'
    elif stability_score >= 50:
        label = 'Moderate'
    else:
        label = 'Low stability'

    components = {
        'sleep_variation_pct': round(sleep_var, 1),
        'weight_fluctuation_pct': round(weight_var, 1),
        'calorie_instability_pct': round(calorie_var, 1),
        'mood_volatility_pct': round(mood_var, 1),
    }

    return {
        'score': stability_score,
        'label': label,
        'components': components,
    }


def detect_health_drift(health_data_list):
    """
    Detect gradual negative trends using recent weekly averages.
    Returns list of drifts with magnitude per week.
    """
    if len(health_data_list) < 4:
        return []

    data = sorted(health_data_list, key=lambda d: d.date)

    # Build weekly buckets
    weekly = {}
    for entry in data:
        year, week, _ = entry.date.isocalendar()
        key = f'{year}-W{week}'
        weekly.setdefault(key, {'dates': [], 'sleep': [], 'exercise': [], 'weight': [], 'calories': []})
        weekly[key]['dates'].append(entry.date)
        if entry.sleep_hours is not None:
            weekly[key]['sleep'].append(entry.sleep_hours)
        if entry.exercise_minutes is not None:
            weekly[key]['exercise'].append(entry.exercise_minutes)
        weekly[key]['weight'].append(entry.weight)
        cal_val = entry.calories_consumed if entry.calories_consumed is not None else entry.total_calories
        if cal_val:
            weekly[key]['calories'].append(cal_val)

    # Keep last 6 weeks for drift detection
    ordered_weeks = sorted(weekly.keys())[-6:]
    if len(ordered_weeks) < 3:
        return []

    def avg(lst):
        return statistics.mean(lst) if lst else None

    drifts = []

    metrics = {
        'sleep': {'label': 'Sleep', 'direction': 'down', 'min_change': 0.3},
        'exercise': {'label': 'Exercise', 'direction': 'down', 'min_change': 10},
        'weight': {'label': 'Weight', 'direction': 'up', 'min_change': 0.3},
        'calories': {'label': 'Calories', 'direction': 'up', 'min_change': 80},
    }

    for metric_key, meta in metrics.items():
        series = []
        for wk in ordered_weeks:
            avg_val = avg(weekly[wk][metric_key])
            if avg_val is not None:
                series.append((wk, avg_val))

        if len(series) < 3:
            continue

        # Simple linear drift: compare first and last average across available weeks
        first_week, first_val = series[0]
        last_week, last_val = series[-1]
        # Weeks between points
        week_gap = max(1, len(series) - 1)
        change_per_week = (last_val - first_val) / week_gap

        # Determine if drift is negative based on direction
        is_negative = change_per_week < -meta['min_change'] if meta['direction'] == 'down' else change_per_week > meta['min_change']
        if not is_negative:
            continue

        severity = abs(change_per_week)
        drifts.append({
            'metric': meta['label'],
            'change_per_week': round(change_per_week, 2),
            'period_weeks': week_gap,
            'from_week': first_week,
            'to_week': last_week,
            'direction': 'decreasing' if change_per_week < 0 else 'increasing',
            'severity': 'High' if severity > meta['min_change'] * 2 else 'Moderate',
            'message': f'{meta["label"]} is {("dropping" if change_per_week < 0 else "rising")} by {abs(change_per_week):.2f} per week over the last {week_gap} weeks.',
        })

    return drifts


def compute_disease_risk_momentum(predictions):
    """
    Compute Health Risk Momentum per disease type from DiseasePrediction queryset.
    Returns list of dicts with per-week change and direction, sorted by absolute change.
    """
    from collections import defaultdict

    if not predictions:
        return []

    grouped = defaultdict(list)
    for p in predictions:
        grouped[p.disease_type].append(p)

    results = []
    for disease, preds in grouped.items():
        if len(preds) < 2:
            continue
        ordered = sorted(preds, key=lambda x: x.created_at)
        first = ordered[0]
        last = ordered[-1]
        days = max(1, (last.created_at.date() - first.created_at.date()).days)
        weeks = max(1.0, days / 7.0)
        change_per_week = (last.risk_score - first.risk_score) / weeks
        direction = 'increasing' if change_per_week > 0 else 'decreasing'
        results.append({
            'disease': disease,
            'change_per_week': round(change_per_week, 2),
            'direction': direction,
            'start_score': round(first.risk_score, 1),
            'end_score': round(last.risk_score, 1),
            'weeks_span': round(weeks, 1),
        })

    results.sort(key=lambda x: abs(x['change_per_week']), reverse=True)
    return results


def estimate_biological_age(user_profile, health_data_list, consistency_summary=None, stability_index=None, recovery_today=None):
    """
    Estimate Biological Age from lifestyle patterns.
    Uses consistency, stability, recovery, sleep, exercise, calories, and BMI.
    Returns chronological age, biological age and key drivers.
    """
    if not health_data_list:
        return {
            'chronological_age': user_profile.age,
            'biological_age': None,
            'delta_years': None,
            'direction': 'unknown',
            'drivers': ['Not enough data to estimate biological age.'],
        }

    data = sorted(health_data_list, key=lambda d: d.date)

    def avg(lst, default=0):
        return statistics.mean(lst) if lst else default

    sleep_avg = avg([d.sleep_hours for d in data if d.sleep_hours is not None], default=7)
    exercise_avg = avg([d.exercise_minutes for d in data if d.exercise_minutes is not None], default=0)
    calories_avg = avg([
        d.calories_consumed if d.calories_consumed is not None else d.total_calories
        for d in data
        if (d.calories_consumed is not None) or d.total_calories
    ], default=user_profile.tdee if hasattr(user_profile, 'tdee') else 2000)
    tdee = user_profile.tdee if hasattr(user_profile, 'tdee') else 2000
    calories_ratio = calories_avg / tdee if tdee else 1.0

    from ml_models.predict_models import predict_recovery_score as ml_predict_recovery
    
    # Use the latest available entry for the ML prediction
    latest_entry = data[-1]
    
    # Execute actual ML Model calculation
    # Linear regression model expects: age, sleep_hours, activity_level, stress_level, daily_steps
    sh = latest_entry.sleep_hours if latest_entry.sleep_hours is not None else sleep_avg
    ex = latest_entry.exercise_minutes if latest_entry.exercise_minutes is not None else exercise_avg
    st = latest_entry.stress_level if latest_entry.stress_level is not None else 5
    stps = latest_entry.daily_steps if latest_entry.daily_steps is not None else 5000
    
    try:
        # Pass the correct arguments matching predict_recovery_score signature
        ml_result = ml_predict_recovery(
            sleep_hours=sh,
            activity_level=ex,
            calories_consumed=calories_avg,
            stress_level=st
        )
        recovery_score = ml_result.get('recovery_score', 65.0)
        
        if consistency_summary is None:
            consistency_summary = calculate_consistency_score(health_data_list)
        consistency_score = consistency_summary.get('score', 60)

        if stability_index is None:
            stability_index = compute_stability_index(health_data_list)
        stability_score = stability_index.get('score') or 60

        lifestyle_score = (
            consistency_score * 0.35 +
            stability_score * 0.3 +
            recovery_score * 0.35
        )
        lifestyle_score = max(0, min(100, lifestyle_score))
        age_adjust = (75 - lifestyle_score) / 5.0
    except Exception:
        # Fallback to pure statistical approach if ML fails
        if consistency_summary is None:
            consistency_summary = calculate_consistency_score(health_data_list)
        consistency_score = consistency_summary.get('score', 60)

        if stability_index is None:
            stability_index = compute_stability_index(health_data_list)
        stability_score = stability_index.get('score') or 60

        recovery_score_val = (recovery_today or {}).get('score') if isinstance(recovery_today, dict) else 65

        lifestyle_score = (
            consistency_score * 0.35 +
            stability_score * 0.3 +
            recovery_score_val * 0.35
        ) / 1.0

        lifestyle_score = max(0, min(100, lifestyle_score))
        age_adjust = (75 - lifestyle_score) / 5.0

    chronological_age = user_profile.age
    raw_biological_age = chronological_age + age_adjust
    
    biological_age = max(chronological_age - 5.0, min(chronological_age + 20.0, raw_biological_age))
    biological_age = round(biological_age, 1)

    delta = round(biological_age - chronological_age, 1)
    abs_delta_years = abs(delta)
    direction = 'older' if delta > 0 else 'younger' if delta < 0 else 'same'

    drivers = []
    if sleep_avg < 6.5:
        drivers.append('Short sleep is pushing your biological age higher.')
    elif 7 <= sleep_avg <= 8.5:
        drivers.append('Consistently good sleep is keeping your biological age younger.')

    if exercise_avg < 30:
        drivers.append('Low daily exercise is reducing metabolic resilience.')
    elif exercise_avg >= 45:
        drivers.append('Strong activity levels are improving cardiovascular age.')

    if calories_ratio > 1.15:
        drivers.append('Calorie intake above your needs is increasing metabolic strain.')
    elif 0.85 <= calories_ratio <= 1.1:
        drivers.append('Calories are well aligned with your energy needs.')

    bmi = user_profile.bmi
    if bmi >= 30:
        drivers.append('High BMI is a major driver of higher biological age.')
    elif 20 <= bmi <= 25:
        drivers.append('Healthy BMI is supporting a younger biological age.')

    if lifestyle_score >= 75:
        drivers.append('Overall lifestyle pattern is excellent for healthy ageing.')
    elif lifestyle_score <= 50:
        drivers.append('Lifestyle volatility suggests higher ageing pressure on the body.')

    return {
        'chronological_age': chronological_age,
        'biological_age': biological_age,
        'delta_years': delta,
        'abs_delta_years': abs_delta_years,
        'direction': direction,
        'lifestyle_score': round(lifestyle_score, 1),
        'drivers': drivers,
    }


def compute_health_balance_dimensions(user_profile, health_data_list, recovery_today=None, stability_index=None):
    """
    Compute scores for Health Balance Radar (0-100 scale):
    Sleep, Exercise, Calories, Stress, Hydration.
    """
    if not health_data_list:
        return {
            'sleep': 0,
            'exercise': 0,
            'calories': 0,
            'stress': 0,
            'hydration': 0,
        }

    data = sorted(health_data_list, key=lambda d: d.date)
    
    # We evaluate balance over the most recent 7-day window if available
    window = data[-7:]
    
    def avg(lst, default=0):
        return statistics.mean(lst) if lst else default

    # 1. Sleep (Aiming for 8 hours -> 100)
    sleep_vals = [d.sleep_hours for d in window if d.sleep_hours is not None]
    avg_sleep = avg(sleep_vals, 0)
    # 0 to 8 hours scales 0-100. Over 8 hours also penalizes slightly (e.g. 10 hours drops score).
    if avg_sleep <= 8:
        sleep_score = (avg_sleep / 8.0) * 100
    else:
        sleep_score = max(0, 100 - ((avg_sleep - 8.0) * 10))
        
    # 2. Exercise (Aiming for 45+ mins -> 100)
    exercise_vals = [d.exercise_minutes for d in window if d.exercise_minutes is not None]
    avg_exercise = avg(exercise_vals, 0)
    exercise_score = min(100.0, (avg_exercise / 45.0) * 100)
    
    # 3. Calories (Aiming to match TDEE)
    tdee = getattr(user_profile, 'tdee', None) or 2000
    calorie_vals = [
        (d.calories_consumed if d.calories_consumed is not None else d.total_calories)
        for d in window if (d.calories_consumed is not None) or d.total_calories
    ]
    avg_calories = avg(calorie_vals, tdee)
    # Deviation from TDEE lowers score
    cal_diff = abs(avg_calories - tdee)
    # 500 calorie diff drops score to 0
    calories_score = max(0.0, 100.0 - (cal_diff / 500.0 * 100))
    
    # 4. Stress (Scale 1-10; 1 -> 100, 10 -> 0)
    stress_vals = [d.stress_level for d in window if d.stress_level is not None]
    avg_stress = avg(stress_vals, 5.0) # default mid stress
    stress_score = max(0.0, 100.0 - ((avg_stress - 1) / 9.0 * 100))
    
    # 5. Hydration (Aiming for 2.5L -> 100)
    water_vals = [d.water_intake_liters for d in window if d.water_intake_liters is not None]
    avg_water = avg(water_vals, 0.0)
    hydration_score = min(100.0, (avg_water / 2.5) * 100)

    return {
        'sleep': round(sleep_score, 1),
        'exercise': round(exercise_score, 1),
        'calories': round(calories_score, 1),
        'stress': round(stress_score, 1),
        'hydration': round(hydration_score, 1),
    }



def calculate_health_risk(profile, recent_health_data):
    """
    Centralized health risk calculation. All modules (Recovery, Overview lifestyle risk,
    alerts) must use this so risk is consistent and never contradictory.

    Point system:
    - BMI: <25 → 0, 25–30 → 10, >30 → 20
    - Sleep: ≥7 hrs → 0, 6–7 → 5, <6 → 10
    - Exercise (weekly): ≥150 min/week → 0, 60–150 → 5, <60 → 10
    - Calorie balance vs TDEE: close → 0, moderate → 5, large imbalance → 10
    - Consistency score: >80 → 0, 60–80 → 5, <60 → 10

    Total risk: 0–15 Low, 16–30 Moderate, >30 High
    """
    def avg(lst, default=0):
        return statistics.mean(lst) if lst else default

    data = sorted(recent_health_data, key=lambda d: d.date) if recent_health_data else []
    tdee = getattr(profile, 'tdee', None) or 2000
    bmi = getattr(profile, 'bmi', None)
    if bmi is None and getattr(profile, 'height', None) and data:
        w = data[-1].weight if data else None
        if w is not None:
            bmi = w / ((profile.height / 100) ** 2)
    if bmi is None:
        bmi = 22.0

    # Consistency score (0–100) from same recent data
    consistency_score_val = 0
    if data:
        consistency_result = calculate_consistency_score(data)
        consistency_score_val = consistency_result.get('score', 0)

    sleep_avg = avg([d.sleep_hours for d in data if d.sleep_hours is not None], default=7)
    exercise_minutes_list = [d.exercise_minutes for d in data if d.exercise_minutes is not None]
    exercise_weekly = sum(exercise_minutes_list) if exercise_minutes_list else 0
    # If we have fewer than 7 days, scale to weekly (e.g. 3 days * 20 min = 60, scale to ~140/week)
    if data and len(data) < 7:
        span_days = max(1, (data[-1].date - data[0].date).days + 1)
        exercise_weekly = exercise_weekly * (7.0 / span_days) if span_days else exercise_weekly
    calories_avg = avg([
        d.calories_consumed if d.calories_consumed is not None else d.total_calories
        for d in data if (d.calories_consumed is not None) or d.total_calories
    ], default=tdee)

    # Points (0, 5, or 10/20)
    if bmi < 25:
        bmi_pts = 0
    elif bmi <= 30:
        bmi_pts = 10
    else:
        bmi_pts = 20

    if sleep_avg >= 7:
        sleep_pts = 0
    elif sleep_avg >= 6:
        sleep_pts = 5
    else:
        sleep_pts = 10

    if exercise_weekly >= 150:
        exercise_pts = 0
    elif exercise_weekly >= 60:
        exercise_pts = 5
    else:
        exercise_pts = 10

    # Calories vs TDEE: within ±200 → 0, ±200–400 → 5, >400 imbalance → 10
    cal_diff = abs(calories_avg - tdee) if tdee else 0
    if cal_diff <= 200:
        calorie_pts = 0
    elif cal_diff <= 400:
        calorie_pts = 5
    else:
        calorie_pts = 10

    if consistency_score_val > 80:
        consistency_pts = 0
    elif consistency_score_val > 60:
        consistency_pts = 5
    else:
        consistency_pts = 10

    total_points = bmi_pts + sleep_pts + exercise_pts + calorie_pts + consistency_pts
    if total_points <= 15:
        risk_level = 'Low'
    elif total_points <= 30:
        risk_level = 'Moderate'
    else:
        risk_level = 'High'

    return {
        'risk_score': total_points,
        'risk_level': risk_level,
        'components': {
            'bmi_points': bmi_pts,
            'sleep_points': sleep_pts,
            'exercise_points': exercise_pts,
            'calorie_points': calorie_pts,
            'consistency_points': consistency_pts,
        },
        'bmi': round(bmi, 1),
        'sleep_avg': round(sleep_avg, 1),
        'exercise_weekly': round(exercise_weekly, 0),
        'calories_avg': round(calories_avg, 0),
        'consistency_score': round(consistency_score_val, 1),
        'tdee': tdee,
    }


def compute_lifestyle_risk_predictions(user_profile, health_data_list, consistency_summary=None, drift_alerts=None):
    """
    Lifestyle-based (non-diagnostic) risk. Uses centralized calculate_health_risk()
    so Recovery and Overview show the same risk level.
    """
    # Use last 30 days of data for risk (or all if less)
    data = sorted(health_data_list, key=lambda d: d.date) if health_data_list else []
    recent = data[-30:] if len(data) > 30 else data
    result = calculate_health_risk(user_profile, recent)
    risk_level = result['risk_level']
    risk_score = result['risk_score']
    base_disclaimer = "Lifestyle-based risk estimate only. Not a diagnosis. Consult a healthcare professional for medical advice."
    drivers = [
        f"Unified risk score: {risk_score} points (0–15 Low, 16–30 Moderate, >30 High)",
        f"BMI {result['bmi']} ({result['components']['bmi_points']} pts) · Sleep {result['sleep_avg']}h ({result['components']['sleep_points']} pts) · Exercise {result['exercise_weekly']} min/week ({result['components']['exercise_points']} pts) · Calories vs TDEE ({result['components']['calorie_points']} pts) · Consistency {result['consistency_score']}% ({result['components']['consistency_points']} pts)",
    ]
    risks = [
        {'condition': 'Diabetes (lifestyle risk)', 'risk_level': risk_level, 'drivers': drivers, 'disclaimer': base_disclaimer},
        {'condition': 'Cholesterol (lifestyle risk)', 'risk_level': risk_level, 'drivers': drivers, 'disclaimer': base_disclaimer},
        {'condition': 'Heart (lifestyle risk)', 'risk_level': risk_level, 'drivers': drivers, 'disclaimer': base_disclaimer},
    ]
    return risks


def suggest_effort_to_impact_actions(user_profile, health_data_list):
    """
    Recommend 1–2 small actions with the best effort-to-impact ratio.
    Impact is heuristic and divided by effort minutes to rank.
    """
    data = sorted(health_data_list, key=lambda d: d.date)

    def avg_metric(values, default=None):
        return round(statistics.mean(values), 2) if values else default

    sleep_avg = avg_metric([d.sleep_hours for d in data if d.sleep_hours is not None], default=7)
    exercise_avg = avg_metric([d.exercise_minutes for d in data if d.exercise_minutes is not None], default=0)
    calories_avg = avg_metric(
        [
            d.calories_consumed if d.calories_consumed is not None else d.total_calories
            for d in data
            if (d.calories_consumed is not None) or d.total_calories
        ],
        default=user_profile.tdee if hasattr(user_profile, 'tdee') else 2000,
    )

    candidates = []

    # Action: +20 min brisk walk (per day)
    if exercise_avg < 40:
        impact = 0.9 if exercise_avg < 20 else 0.7
        effort = 20
        candidates.append({
            'title': 'Add 20 min brisk walk',
            'explanation': 'Boosts cardio fitness with low joint stress and minimal prep.',
            'effort_minutes': effort,
            'impact_score': impact,
        })

    # Action: sleep +30 minutes
    if sleep_avg < 7.5:
        impact = 0.75 if sleep_avg < 7 else 0.6
        effort = 30
        candidates.append({
            'title': 'Sleep 30 mins earlier',
            'explanation': 'Improves recovery and hormonal balance with small schedule shift.',
            'effort_minutes': effort,
            'impact_score': impact,
        })

    # Action: swap sugary drink
    if calories_avg and calories_avg > user_profile.tdee * 0.95:
        candidates.append({
            'title': 'Swap one sugary drink for water',
            'explanation': 'Removes 100–150 daily calories without extra time investment.',
            'effort_minutes': 5,
            'impact_score': 0.55,
        })

    # Action: 10-minute mobility
    candidates.append({
        'title': '10 min mobility break',
        'explanation': 'Reduces stiffness and improves exercise readiness; easy to fit in.',
        'effort_minutes': 10,
        'impact_score': 0.35,
    })

    # Rank by impact/effort ratio
    for c in candidates:
        c['ratio'] = round(c['impact_score'] / max(c['effort_minutes'], 1), 3)

    top_actions = sorted(candidates, key=lambda c: (c['ratio'], c['impact_score']), reverse=True)[:2]
    return top_actions


def assess_progress(user_profile, health_data_list):
    """Assess user progress and provide status"""
    if not health_data_list or len(health_data_list) < 2:
        return {
            'status': 'insufficient_data',
            'message': 'Add more data to track progress',
            'improvement': 0
        }
    
    # Ensure chronological order and retrieve the two latest records
    recent_entries = sorted(health_data_list, key=lambda d: d.date)
    previous_entry = recent_entries[-2]
    current_entry = recent_entries[-1]
    
    current_weight = current_entry.weight
    previous_weight = previous_entry.weight
    
    # Calculate difference correctly
    weight_change = current_weight - previous_weight
    weight_change_pct = (weight_change / previous_weight) * 100 if previous_weight > 0 else 0
    
    # Progress message rules
    if weight_change < 0:
        status = 'good'
        message = f'Good progress! Lost {abs(weight_change):.1f} kg'
    elif weight_change > 0:
        status = 'needs_improvement'
        message = f'Weight increased by {weight_change:.1f} kg. Review your plan.'
    else:
        status = 'maintaining'
        message = 'Weight unchanged.'
    
    return {
        'status': status,
        'message': message,
        'weight_change': round(weight_change, 1),
        'weight_change_pct': round(weight_change_pct, 1),
        'improvement': -weight_change if user_profile.health_goal == 'weight_loss' else weight_change
    }


def assess_health_risks(user_profile, health_data_list):
    """
    Assess health risks and generate alerts. Uses centralized calculate_health_risk()
    so risk_level on all alerts matches Overview and Recovery (no conflicting Low vs High).
    """
    alerts = []
    recent = list(health_data_list)[-30:] if health_data_list else []
    unified = calculate_health_risk(user_profile, recent)
    # Use same risk level for all alerts (Low -> low, Moderate -> medium, High -> high)
    risk_level = unified['risk_level'].lower()
    if risk_level == 'moderate':
        risk_level = 'medium'

    # BMI Risk
    if user_profile.bmi < 18.5:
        alerts.append({
            'risk_level': risk_level,
            'alert_type': 'bmi',
            'message': f'Your BMI is {user_profile.bmi:.1f} (Underweight). Consider consulting a healthcare provider.',
            'recommendations': ['Increase calorie intake', 'Focus on nutrient-dense foods', 'Consult nutritionist']
        })
    elif user_profile.bmi > 30:
        alerts.append({
            'risk_level': risk_level,
            'alert_type': 'bmi',
            'message': f'Your BMI is {user_profile.bmi:.1f} (Obese). This increases risk of various health conditions.',
            'recommendations': ['Weight loss program', 'Regular exercise', 'Consult healthcare provider', 'Diet modification']
        })
    elif user_profile.bmi > 25:
        alerts.append({
            'risk_level': risk_level,
            'alert_type': 'bmi',
            'message': f'Your BMI is {user_profile.bmi:.1f} (Overweight). Consider weight management.',
            'recommendations': ['Increase physical activity', 'Calorie deficit', 'Regular exercise']
        })

    # Sleep Risk
    if health_data_list:
        sleep_data = [d.sleep_hours for d in health_data_list if d.sleep_hours]
        if sleep_data:
            avg_sleep = sum(sleep_data) / len(sleep_data)
            if avg_sleep < 6:
                alerts.append({
                    'risk_level': risk_level,
                    'alert_type': 'sleep',
                    'message': f'Average sleep is only {avg_sleep:.1f} hours. Chronic sleep deprivation increases disease risk.',
                    'recommendations': ['Improve sleep schedule', 'Aim for 7-9 hours', 'Sleep hygiene practices', 'Consult sleep specialist if persistent']
                })
            elif avg_sleep < 7:
                alerts.append({
                    'risk_level': risk_level,
                    'alert_type': 'sleep',
                    'message': f'Average sleep is {avg_sleep:.1f} hours. Aim for 7-9 hours for optimal health.',
                    'recommendations': ['Improve sleep duration', 'Consistent sleep schedule', 'Better sleep hygiene']
                })

    # Exercise Risk
    if health_data_list:
        exercise_data = [d.exercise_minutes for d in health_data_list if d.exercise_minutes and d.exercise_minutes > 0]
        if exercise_data:
            avg_exercise = sum(exercise_data) / len(exercise_data)
            if avg_exercise < 20:
                alerts.append({
                    'risk_level': risk_level,
                    'alert_type': 'exercise',
                    'message': f'Average exercise is only {avg_exercise:.0f} minutes/day. Insufficient physical activity increases health risks.',
                    'recommendations': ['Increase exercise to 30+ minutes daily', 'Start with walking', 'Gradually increase intensity', 'Consult fitness trainer']
                })
        elif user_profile.activity_level in ['sedentary', 'light']:
            alerts.append({
                'risk_level': risk_level,
                'alert_type': 'exercise',
                'message': 'Low activity level detected. Regular exercise is essential for health.',
                'recommendations': ['Start with 15-20 min daily', 'Gradually increase', 'Find activities you enjoy']
            })

    return alerts


def predict_disease_risks(user_profile, health_data_list):
    """Predict disease risks using ML model"""
    model = DiseasePredictionModel()
    
    # Calculate averages from health data
    sleep_data = [d.sleep_hours for d in health_data_list if d.sleep_hours]
    exercise_data = [d.exercise_minutes for d in health_data_list if d.exercise_minutes and d.exercise_minutes > 0]
    calories_data = [d.calories_consumed for d in health_data_list if d.calories_consumed]
    
    avg_sleep = sum(sleep_data) / len(sleep_data) if sleep_data else 7
    exercise_frequency = len(exercise_data) / len(health_data_list) if health_data_list else 0.5
    diet_quality = 0.7  # Default, can be improved with more data
    
    predictions = model.predict_risk(
        user_profile.age,
        user_profile.bmi,
        user_profile.activity_level,
        avg_sleep,
        exercise_frequency,
        diet_quality,
        0  # family_history - can be added to profile later
    )
    
    return predictions

def compute_recovery_score_7day(profile, health_data):
    if not health_data:
        return 50

    # Last 7 days data
    last7 = health_data[:7]

    sleep_avg = sum([d.sleep_hours or 0 for d in last7]) / len(last7)
    exercise_total = sum([d.exercise_minutes or 0 for d in last7])
    calories_avg = sum([d.calories_consumed or 0 for d in last7]) / len(last7)
    weights = [d.weight for d in last7 if d.weight]

    # Sleep Score
    if sleep_avg >= 7:
        sleep_score = 30
    elif sleep_avg >= 6:
        sleep_score = 20
    elif sleep_avg >= 5:
        sleep_score = 10
    else:
        sleep_score = 5

    # Exercise Score
    if exercise_total >= 150:
        exercise_score = 25
    elif exercise_total >= 90:
        exercise_score = 18
    elif exercise_total >= 60:
        exercise_score = 12
    else:
        exercise_score = 5

    # Calorie Score
    tdee = profile.tdee
    diff = abs(calories_avg - tdee)

    if diff <= 200:
        calorie_score = 25
    elif diff <= 400:
        calorie_score = 15
    else:
        calorie_score = 5

    # Weight Trend
    if len(weights) >= 2:
        change = weights[-1] - weights[0]
    else:
        change = 0

    if change <= 0:
        weight_score = 20
    elif change <= 2:
        weight_score = 12
    else:
        weight_score = 5

    score = sleep_score + exercise_score + calorie_score + weight_score

    if score >= 80:
        status = "Excellent"
    elif score >= 60:
        status = "Good"
    elif score >= 40:
        status = "Moderate"
    else:
        status = "Poor"

    return {
        "score": score,
        "status": status,
        "sleep_score": sleep_score,
        "exercise_score": exercise_score,
        "calorie_score": calorie_score,
        "weight_score": weight_score,
    }


