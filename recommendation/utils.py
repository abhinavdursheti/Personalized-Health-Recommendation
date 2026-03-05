"""
Utility functions for recommendation system
"""
import statistics
import json

from .ml_models.diet_model import DietRecommendationModel


def calculate_recovery_score(health_data, profile):
    """
    Health Recovery Score (0-100) from sleep, activity, calories, and stress proxy.
    Stress is inferred from sleep quality and activity (smartwatch-style metric).
    Returns dict: { 'score': int 0-100, 'label': str }
    """
    if health_data is None:
        return {'score': None, 'label': 'No data'}

    # Sleep quality: 0-30 points
    sleep_hours = health_data.sleep_hours
    if sleep_hours is None:
        sleep_score = 0
    elif 7 <= sleep_hours <= 8:
        sleep_score = 30
    elif 6 <= sleep_hours < 7 or 8 < sleep_hours <= 9:
        sleep_score = 22
    elif 5 <= sleep_hours < 6 or 9 < sleep_hours <= 10:
        sleep_score = 14
    else:
        sleep_score = 5

    # Activity: 0-25 points
    exercise_minutes = health_data.exercise_minutes or 0
    if exercise_minutes >= 30:
        activity_score = 25
    elif exercise_minutes >= 15:
        activity_score = 18
    elif exercise_minutes >= 1:
        activity_score = 10
    else:
        activity_score = 0

    # Calories vs TDEE: 0-25 points
    tdee = profile.tdee
    calories = health_data.total_calories or health_data.calories_consumed
    if calories is None or tdee is None or tdee <= 0:
        calorie_score = 12  # neutral when no data
    else:
        ratio = calories / tdee
        if 0.85 <= ratio <= 1.15:
            calorie_score = 25
        elif 0.75 <= ratio <= 1.25:
            calorie_score = 18
        elif 0.6 <= ratio <= 1.4:
            calorie_score = 10
        else:
            calorie_score = 5

    # Stress proxy (0-20): recovery readiness from sleep + activity
    stress_score = round((sleep_score / 30.0) * 10 + (activity_score / 25.0) * 10)

    total = sleep_score + activity_score + calorie_score + stress_score
    score = min(100, total)

    if score >= 80:
        label = 'Excellent'
    elif score >= 60:
        label = 'Good'
    elif score >= 40:
        label = 'Fair'
    else:
        label = 'Poor recovery'

    return {'score': score, 'label': label}
from .ml_models.exercise_model import ExerciseRecommendationModel
from .ml_models.sleep_model import SleepRecommendationModel
from .ml_models.recovery_stability_model import RecoveryStabilityModel
from .ml_models.correlation_model import CorrelationModel
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
    Generate recovery and stability analysis from recent health data (last 7–14 days).
    Uses sleep, exercise, calories and logging behavior to derive:
    - recovery_days (1–14)
    - stability_score (0–100)
    - consistency_score (0–100)
    - streak_days (current logging streak)
    - risk_level (Low / Medium / High)
    - recommendations (behavior-based)
    """
    from datetime import timedelta

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

    # Sort by date and focus on a recent 14‑day window (or fewer if limited data)
    data = sorted(health_data_list, key=lambda d: d.date)
    end_date = data[-1].date
    window_start = end_date - timedelta(days=13)
    window = [d for d in data if d.date >= window_start] or data[-min(7, len(data)):]

    # Helper series
    def _avg(values):
        return statistics.mean(values) if values else 0.0

    sleep_values = [d.sleep_hours for d in window if d.sleep_hours is not None]
    exercise_values = [d.exercise_minutes for d in window if d.exercise_minutes is not None]
    calorie_values = [
        (d.calories_consumed if d.calories_consumed is not None else d.total_calories)
        for d in window
        if (d.calories_consumed is not None) or d.total_calories
    ]
    weight_values = [d.weight for d in window if d.weight is not None]

    avg_sleep = _avg(sleep_values)
    avg_exercise = _avg(exercise_values)
    avg_calories = _avg(calorie_values)

    # --- Recovery days: better sleep + balanced calories => faster recovery; very high training load slows it ---
    # Sleep factor (0.4–1.0)
    if avg_sleep <= 0:
        sleep_factor = 0.6
    elif 7 <= avg_sleep <= 8:
        sleep_factor = 1.0
    elif 6 <= avg_sleep < 7 or 8 < avg_sleep <= 9:
        sleep_factor = 0.85
    elif 5 <= avg_sleep < 6 or 9 < avg_sleep <= 10:
        sleep_factor = 0.7
    else:
        sleep_factor = 0.5

    # Calorie balance factor (0.4–1.0) relative to TDEE
    tdee = getattr(user_profile, 'tdee', None)
    if tdee and avg_calories:
        ratio = avg_calories / tdee
        if 0.9 <= ratio <= 1.1:
            cal_factor = 1.0
        elif 0.8 <= ratio <= 1.2:
            cal_factor = 0.85
        elif 0.7 <= ratio <= 1.3:
            cal_factor = 0.7
        else:
            cal_factor = 0.5
    else:
        cal_factor = 0.7

    # Training load / fatigue factor (0.7–1.4) from average daily exercise minutes
    if avg_exercise <= 20:
        fatigue_factor = 0.8
    elif avg_exercise <= 40:
        fatigue_factor = 1.0
    elif avg_exercise <= 60:
        fatigue_factor = 1.2
    else:
        fatigue_factor = 1.4

    base_recovery = 5.0
    denominator = max(0.4, sleep_factor * 0.6 + cal_factor * 0.4)
    raw_recovery_days = base_recovery * fatigue_factor / denominator
    recovery_days = max(1.0, min(14.0, round(raw_recovery_days, 1)))

    # --- Stability & consistency metrics reused from helpers (0–100) ---
    consistency_result = calculate_consistency_score(window)
    consistency_score = consistency_result['score']
    details = consistency_result.get('details', {})
    missed_days = details.get('missed_days', 0)
    total_span_days = details.get('total_span_days', len({d.date for d in window}))
    adherence_rate = 0.0
    if total_span_days:
        adherence_rate = round((total_span_days - missed_days) / total_span_days, 2)

    stability_index = compute_stability_index(window)
    stability_score = stability_index.get('score')
    if stability_score is None:
        stability_score = 50  # neutral when not enough variation data
    stability_score = round(stability_score, 1)

    # --- Current logging streak (consecutive calendar days with any entry) ---
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

    # --- Risk level from stability score as requested ---
    if stability_score > 80:
        risk_level = 'Low'
    elif 50 <= stability_score <= 80:
        risk_level = 'Medium'
    else:
        risk_level = 'High'

    is_stable = stability_score >= 50

    # --- Behavior-based recommendations ---
    recommendations = []

    if avg_sleep and avg_sleep < 6:
        recommendations.append("Improve sleep duration for better recovery (aim for 7–8 hours).")
    elif avg_sleep and avg_sleep > 9:
        recommendations.append("Your sleep duration is quite high; focus on consistent 7–8 hours for optimal recovery.")

    if avg_exercise < 20:
        recommendations.append("Increase physical activity for improved health (target at least 20–30 minutes most days).")
    elif avg_exercise > 60:
        recommendations.append("Your training load is high; schedule deliberate rest or light days to avoid overtraining.")

    if tdee and avg_calories:
        cal_ratio = avg_calories / tdee
        if cal_ratio < 0.8:
            recommendations.append("Your calorie deficit is high; maintain a more balanced intake to support recovery.")
        elif cal_ratio > 1.2:
            recommendations.append("Your calorie intake is above your needs; reduce surplus to avoid long‑term weight gain.")

    if consistency_score < 50:
        recommendations.append("Work on logging most days each week to build consistent habits.")
    elif consistency_score < 75:
        recommendations.append("Your consistency is moderate; try to reduce missed days to stabilize recovery.")

    if stability_score < 50:
        recommendations.append("Large swings in sleep, weight, or calories reduce stability; aim for smaller day‑to‑day changes.")

    if not recommendations:
        recommendations.append("Your recovery and stability look solid. Maintain your current routine and track progress.")

    metrics = {
        'window_days': total_span_days,
        'avg_sleep': round(avg_sleep, 1) if avg_sleep else None,
        'avg_exercise_minutes': round(avg_exercise, 1) if avg_exercise else None,
        'avg_calories': round(avg_calories, 0) if avg_calories else None,
        'has_weight_data': bool(weight_values),
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


def generate_correlation_analysis(health_data_list):
    """Generate behavior-cause correlation analysis"""
    model = CorrelationModel()
    return model.analyze_correlations(health_data_list)


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

    if consistency_summary is None:
        consistency_summary = calculate_consistency_score(health_data_list)
    consistency_score = consistency_summary.get('score', 60)

    if stability_index is None:
        stability_index = compute_stability_index(health_data_list)
    stability_score = stability_index.get('score') or 60

    recovery_score = (recovery_today or {}).get('score') if isinstance(recovery_today, dict) else None
    if recovery_score is None:
        recovery_score = 65

    lifestyle_score = (
        consistency_score * 0.35 +
        stability_score * 0.3 +
        recovery_score * 0.35
    ) / 1.0

    lifestyle_score = max(0, min(100, lifestyle_score))

    # Map lifestyle_score (0–100) to age adjustment roughly between about -10 and +10 years
    age_adjust = (75 - lifestyle_score) / 7.0
    chronological_age = user_profile.age
    biological_age = round(chronological_age + age_adjust, 1)

    delta = round(biological_age - chronological_age, 1)
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
        'direction': direction,
        'lifestyle_score': round(lifestyle_score, 1),
        'drivers': drivers,
    }


def compute_health_balance_dimensions(user_profile, health_data_list, recovery_today=None, stability_index=None):
    """
    Compute scores for Health Balance Radar:
    Sleep, Exercise, Nutrition, Recovery, Stability, Metabolic (0–100 each).
    """
    if not health_data_list:
        return {
            'sleep': 0,
            'exercise': 0,
            'nutrition': 0,
            'recovery': 0,
            'stability': 0,
            'metabolic': 0,
        }

    consistency = calculate_consistency_score(health_data_list)
    details = consistency.get('details', {})
    sleep_score = details.get('sleep_score', 0)
    exercise_score = details.get('exercise_score', 0)
    diet_score = details.get('diet_score', 0)

    rec_score = (recovery_today or {}).get('score') if isinstance(recovery_today, dict) else None
    if rec_score is None:
        rec_score = 65

    stab_score = (stability_index or {}).get('score') if isinstance(stability_index, dict) else None
    if stab_score is None:
        stab_score = 60

    # Simple metabolic health proxy from BMI and calories balance
    data = sorted(health_data_list, key=lambda d: d.date)

    def avg(lst, default=0):
        return statistics.mean(lst) if lst else default

    bmi = user_profile.bmi
    if bmi < 19 or bmi > 32:
        metabolic = 45
    elif 19 <= bmi <= 27:
        metabolic = 85
    else:
        metabolic = 70

    calories_avg = avg([
        d.calories_consumed if d.calories_consumed is not None else d.total_calories
        for d in data
        if (d.calories_consumed is not None) or d.total_calories
    ], default=user_profile.tdee if hasattr(user_profile, 'tdee') else 2000)
    tdee = user_profile.tdee if hasattr(user_profile, 'tdee') else 2000
    if tdee:
        ratio = calories_avg / tdee
        if ratio > 1.25 or ratio < 0.75:
            metabolic -= 10

    return {
        'sleep': round(sleep_score, 1),
        'exercise': round(exercise_score, 1),
        'nutrition': round(diet_score, 1),
        'recovery': round(rec_score, 1),
        'stability': round(stab_score, 1),
        'metabolic': max(0, min(100, round(metabolic, 1))),
    }



def compute_lifestyle_risk_predictions(user_profile, health_data_list, consistency_summary=None, drift_alerts=None):
    """
    Lifestyle-based (non-diagnostic) risk classification for Diabetes, Cholesterol, Heart.
    Uses trends in BMI, sleep, exercise, calories, consistency, and drifts.
    """
    if consistency_summary is None:
        consistency_summary = calculate_consistency_score(health_data_list)
    if drift_alerts is None:
        drift_alerts = detect_health_drift(health_data_list)

    data = sorted(health_data_list, key=lambda d: d.date)

    def avg(lst, default=0):
        return statistics.mean(lst) if lst else default

    bmi_latest = user_profile.bmi
    bmi_trend = 0
    if len(data) >= 2:
        bmi_first = data[0].weight / ((user_profile.height / 100) ** 2)
        bmi_trend = bmi_latest - bmi_first

    sleep_avg = avg([d.sleep_hours for d in data if d.sleep_hours is not None], default=7)
    exercise_avg = avg([d.exercise_minutes for d in data if d.exercise_minutes is not None], default=0)
    calories_avg = avg([
        d.calories_consumed if d.calories_consumed is not None else d.total_calories
        for d in data if (d.calories_consumed is not None) or d.total_calories
    ], default=user_profile.tdee if hasattr(user_profile, 'tdee') else 2000)
    calories_surplus = calories_avg - (user_profile.tdee if hasattr(user_profile, 'tdee') else 2000)

    drift_flags = {
        'weight_up': any(d['metric'] == 'Weight' and d['direction'] == 'increasing' for d in drift_alerts),
        'sleep_down': any(d['metric'] == 'Sleep' and d['direction'] == 'decreasing' for d in drift_alerts),
        'exercise_down': any(d['metric'] == 'Exercise' and d['direction'] == 'decreasing' for d in drift_alerts),
    }

    consistency_score = consistency_summary.get('score', 0)

    def classify_risk(points):
        if points >= 4:
            return 'High'
        if points >= 2:
            return 'Moderate'
        return 'Low'

    risks = []
    base_disclaimer = "Lifestyle-based risk estimate only. Not a diagnosis. Consult a healthcare professional for medical advice."

    # Diabetes
    diabetes_points = 0
    if bmi_latest >= 30 or bmi_trend > 1:
        diabetes_points += 2
    elif bmi_latest >= 27:
        diabetes_points += 1
    if sleep_avg < 6:
        diabetes_points += 2
    elif sleep_avg < 7:
        diabetes_points += 1
    if exercise_avg < 30:
        diabetes_points += 2
    elif exercise_avg < 60:
        diabetes_points += 1
    if calories_surplus > 200:
        diabetes_points += 1
    if consistency_score < 50:
        diabetes_points += 1
    if drift_flags['weight_up'] or drift_flags['sleep_down']:
        diabetes_points += 1
    risks.append({
        'condition': 'Diabetes (lifestyle risk)',
        'risk_level': classify_risk(diabetes_points),
        'drivers': [
            f'BMI {bmi_latest:.1f} (trend {"+" if bmi_trend>=0 else ""}{bmi_trend:.1f})',
            f'Sleep avg {sleep_avg:.1f}h',
            f'Exercise avg {exercise_avg:.0f} min',
            f'Calories vs TDEE: {calories_surplus:+.0f} cal',
            f'Consistency score: {consistency_score:.0f}',
        ],
        'disclaimer': base_disclaimer,
    })

    # Cholesterol
    chol_points = 0
    if bmi_latest >= 30:
        chol_points += 2
    elif bmi_latest >= 27:
        chol_points += 1
    if calories_surplus > 200:
        chol_points += 2
    elif calories_surplus > 50:
        chol_points += 1
    if exercise_avg < 40:
        chol_points += 2
    elif exercise_avg < 80:
        chol_points += 1
    if sleep_avg < 6.5:
        chol_points += 1
    if drift_flags['weight_up'] or drift_flags['exercise_down']:
        chol_points += 1
    risks.append({
        'condition': 'Cholesterol (lifestyle risk)',
        'risk_level': classify_risk(chol_points),
        'drivers': [
            f'BMI {bmi_latest:.1f}',
            f'Calories vs TDEE: {calories_surplus:+.0f} cal',
            f'Exercise avg {exercise_avg:.0f} min',
            f'Sleep avg {sleep_avg:.1f}h',
            f'Drift signals: weight up {drift_flags["weight_up"]}, exercise down {drift_flags["exercise_down"]}',
        ],
        'disclaimer': base_disclaimer,
    })

    # Heart
    heart_points = 0
    if bmi_latest >= 30:
        heart_points += 2
    elif bmi_latest >= 27:
        heart_points += 1
    if exercise_avg < 30:
        heart_points += 2
    elif exercise_avg < 60:
        heart_points += 1
    if sleep_avg < 6.5:
        heart_points += 1
    if consistency_score < 50:
        heart_points += 1
    if drift_flags['weight_up'] or drift_flags['sleep_down'] or drift_flags['exercise_down']:
        heart_points += 1
    risks.append({
        'condition': 'Heart (lifestyle risk)',
        'risk_level': classify_risk(heart_points),
        'drivers': [
            f'BMI {bmi_latest:.1f} (trend {"+" if bmi_trend>=0 else ""}{bmi_trend:.1f})',
            f'Exercise avg {exercise_avg:.0f} min',
            f'Sleep avg {sleep_avg:.1f}h',
            f'Consistency score: {consistency_score:.0f}',
            f'Drift signals: weight up {drift_flags["weight_up"]}, sleep down {drift_flags["sleep_down"]}',
        ],
        'disclaimer': base_disclaimer,
    })

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
    
    # Get first and last entries
    first_entry = health_data_list[0]
    last_entry = health_data_list[-1]
    
    # Calculate weight change
    weight_change = last_entry.weight - first_entry.weight
    weight_change_pct = (weight_change / first_entry.weight) * 100 if first_entry.weight > 0 else 0
    
    # Determine status based on goal
    if user_profile.health_goal == 'weight_loss':
        if weight_change < -1:
            status = 'excellent'
            message = f'Great progress! Lost {abs(weight_change):.1f} kg'
        elif weight_change < 0:
            status = 'good'
            message = f'Good progress! Lost {abs(weight_change):.1f} kg'
        elif weight_change < 1:
            status = 'maintaining'
            message = 'Weight is stable. Keep going!'
        else:
            status = 'needs_improvement'
            message = f'Weight increased by {weight_change:.1f} kg. Review your plan.'
    elif user_profile.health_goal == 'muscle_gain':
        if weight_change > 1:
            status = 'excellent'
            message = f'Great progress! Gained {weight_change:.1f} kg'
        elif weight_change > 0:
            status = 'good'
            message = f'Good progress! Gained {weight_change:.1f} kg'
        elif weight_change > -0.5:
            status = 'maintaining'
            message = 'Weight is stable. Increase calories and exercise.'
        else:
            status = 'needs_improvement'
            message = f'Weight decreased by {abs(weight_change):.1f} kg. Increase calorie intake.'
    else:  # maintenance or general
        if abs(weight_change) < 1:
            status = 'excellent'
            message = 'Excellent! Weight is well maintained.'
        elif abs(weight_change) < 2:
            status = 'good'
            message = 'Good! Weight is relatively stable.'
        else:
            status = 'needs_improvement'
            message = f'Weight changed by {abs(weight_change):.1f} kg. Focus on consistency.'
    
    return {
        'status': status,
        'message': message,
        'weight_change': round(weight_change, 1),
        'weight_change_pct': round(weight_change_pct, 1),
        'improvement': weight_change if user_profile.health_goal == 'weight_loss' else -weight_change
    }


def assess_health_risks(user_profile, health_data_list):
    """Assess health risks and generate alerts"""
    alerts = []
    
    # BMI Risk
    if user_profile.bmi < 18.5:
        alerts.append({
            'risk_level': 'medium',
            'alert_type': 'bmi',
            'message': f'Your BMI is {user_profile.bmi:.1f} (Underweight). Consider consulting a healthcare provider.',
            'recommendations': ['Increase calorie intake', 'Focus on nutrient-dense foods', 'Consult nutritionist']
        })
    elif user_profile.bmi > 30:
        alerts.append({
            'risk_level': 'high',
            'alert_type': 'bmi',
            'message': f'Your BMI is {user_profile.bmi:.1f} (Obese). This increases risk of various health conditions.',
            'recommendations': ['Weight loss program', 'Regular exercise', 'Consult healthcare provider', 'Diet modification']
        })
    elif user_profile.bmi > 25:
        alerts.append({
            'risk_level': 'medium',
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
                    'risk_level': 'high',
                    'alert_type': 'sleep',
                    'message': f'Average sleep is only {avg_sleep:.1f} hours. Chronic sleep deprivation increases disease risk.',
                    'recommendations': ['Improve sleep schedule', 'Aim for 7-9 hours', 'Sleep hygiene practices', 'Consult sleep specialist if persistent']
                })
            elif avg_sleep < 7:
                alerts.append({
                    'risk_level': 'medium',
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
                    'risk_level': 'high',
                    'alert_type': 'exercise',
                    'message': f'Average exercise is only {avg_exercise:.0f} minutes/day. Insufficient physical activity increases health risks.',
                    'recommendations': ['Increase exercise to 30+ minutes daily', 'Start with walking', 'Gradually increase intensity', 'Consult fitness trainer']
                })
        elif user_profile.activity_level in ['sedentary', 'light']:
            alerts.append({
                'risk_level': 'medium',
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

