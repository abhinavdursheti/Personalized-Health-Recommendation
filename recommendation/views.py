from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
import json

from .models import UserProfile, HealthData, Recommendation, RecoveryStabilityAnalysis, BehaviorCorrelationAnalysis, HabitSensitivityAnalysis, Reminder, HealthRiskAlert, DiseasePrediction, FoodEntry
from .food_database import calculate_nutrition, get_food_suggestions, get_food_replacements
from .utils import (
    generate_diet_recommendation, generate_exercise_recommendation, generate_sleep_recommendation,
    generate_recovery_stability_analysis, generate_correlation_analysis, generate_habit_sensitivity_analysis,
    assess_progress, assess_health_risks, predict_disease_risks, calculate_consistency_score,
    detect_health_drift, suggest_effort_to_impact_actions, compute_lifestyle_risk_predictions,
    calculate_recovery_score, compute_recovery_score_7day, compute_stability_index, compute_disease_risk_momentum,
    estimate_biological_age, compute_health_balance_dimensions, calculate_health_risk,
)
from .ml_models.simulator_model import HealthSimulatorModel


def index(request):
    """Home page"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'index.html')


@login_required
def dashboard(request):
    """Default dashboard entry -> overview dashboard."""
    return dashboard_overview(request)


def _build_dashboard_context(request):
    """Collect shared dashboard data for reuse across multiple dashboard pages."""
    profile = request.user.userprofile

    # Health data
    health_data_list = list(HealthData.objects.filter(user=request.user).order_by('date'))
    recent_data = HealthData.objects.filter(user=request.user)[:7]

    # Progress series (last 30 entries)
    progress_data = {'weight_trend': [], 'sleep_trend': [], 'exercise_trend': []}
    for data in health_data_list[:30]:
        progress_data['weight_trend'].append({'date': data.date.isoformat(), 'weight': data.weight})
        if data.sleep_hours:
            progress_data['sleep_trend'].append({'date': data.date.isoformat(), 'hours': data.sleep_hours})
        if data.exercise_minutes:
            progress_data['exercise_trend'].append({'date': data.date.isoformat(), 'minutes': data.exercise_minutes})

    # Analytics
    progress_assessment = assess_progress(profile, list(health_data_list))
    consistency_summary = calculate_consistency_score(list(health_data_list))
    drift_alerts = detect_health_drift(list(health_data_list))
    effort_actions = suggest_effort_to_impact_actions(profile, list(health_data_list))
    lifestyle_risks = compute_lifestyle_risk_predictions(profile, list(health_data_list), consistency_summary, drift_alerts)

    # Recommendations
    recommendations = Recommendation.objects.filter(user=request.user, is_active=True)[:3]

    # Risk alerts
    risk_alerts = HealthRiskAlert.objects.filter(user=request.user, is_read=False).order_by('-created_at')[:5]

    # Reminders
    reminders = Reminder.objects.filter(user=request.user, is_active=True).order_by('time')

    # Disease predictions
    disease_predictions = DiseasePrediction.objects.filter(user=request.user).order_by('-created_at')[:3]

    # Food / nutrition
    from datetime import date
    today = date.today()
    today_food_entries = FoodEntry.objects.filter(user=request.user, date=today).order_by('meal_type')
    today_health_data = HealthData.objects.filter(user=request.user, date=today).first()
    food_by_meal = {
        'breakfast': today_food_entries.filter(meal_type='breakfast'),
        'lunch': today_food_entries.filter(meal_type='lunch'),
        'dinner': today_food_entries.filter(meal_type='dinner'),
        'snacks': today_food_entries.filter(meal_type='snacks'),
    }

    # Auto-generate risk alerts if needed
    if health_data_list:
        new_alerts = assess_health_risks(profile, list(health_data_list))
        for alert_data in new_alerts:
            existing = HealthRiskAlert.objects.filter(
                user=request.user,
                alert_type=alert_data['alert_type'],
                is_read=False
            ).first()
            if not existing:
                HealthRiskAlert.objects.create(
                    user=request.user,
                    risk_level=alert_data['risk_level'],
                    alert_type=alert_data['alert_type'],
                    message=alert_data['message'],
                    recommendations=alert_data['recommendations']
                )

    # Health Recovery Score (latest, previous, and last 7 days - data-driven)
    recent_health_records = HealthData.objects.filter(user=request.user).order_by('-date')[:2]
    today_data = recent_health_records[0] if len(recent_health_records) > 0 else None
    yesterday_data = recent_health_records[1] if len(recent_health_records) > 1 else None
    
    recovery_today = calculate_recovery_score(today_data, profile)
    recovery_yesterday = calculate_recovery_score(yesterday_data, profile)
    recovery_7day = compute_recovery_score_7day(profile, list(health_data_list))

    # Health Stability Index (predictive behavior score)
    stability_index = compute_stability_index(health_data_list)

    # ----- ML Model Predictions -----
    ml_predictions = None
    try:
        from ml_models.predict_models import (
            predict_lifestyle_risk,
            predict_recovery_score,
            predict_exercise_category,
        )
        # Use the latest health data entry that has the required fields
        latest_with_ml = (
            HealthData.objects.filter(user=request.user)
            .exclude(sleep_hours__isnull=True)
            .exclude(exercise_minutes__isnull=True)
            .order_by('-date')
            .first()
        )
        if latest_with_ml:
            age = profile.age
            sleep_hours_val = latest_with_ml.sleep_hours or 7.0
            activity_level_val = latest_with_ml.exercise_minutes or 30
            stress_level_val = latest_with_ml.stress_level or 5
            daily_steps_val = latest_with_ml.daily_steps or 5000
            
            tdee_val = getattr(profile, 'tdee', None) or 2000
            calories_consumed_val = (
                latest_with_ml.calories_consumed 
                if latest_with_ml.calories_consumed is not None 
                else latest_with_ml.total_calories if latest_with_ml.total_calories > 0 else tdee_val
            )

            lifestyle_dict = predict_lifestyle_risk(profile.bmi, age, sleep_hours_val, activity_level_val, stress_level_val, daily_steps_val)
            recovery_dict = predict_recovery_score(sleep_hours_val, activity_level_val, calories_consumed_val, stress_level_val)
            exercise_dict = predict_exercise_category(profile.bmi, age, sleep_hours_val, activity_level_val, stress_level_val, daily_steps_val)

            lifestyle_risk = lifestyle_dict.get('risk_label', 'Unknown')
            recovery_score = recovery_dict.get('recovery_score', 0)
            
            # --- Consistency Adjustment Layer ---
            # If a user is significantly obese/overweight, their recovery score should reflect reality.
            if lifestyle_risk == "Obese" or profile.bmi >= 30:
                recovery_score = min(recovery_score, 60)
            elif lifestyle_risk == "Overweight":
                recovery_score = min(recovery_score, 75)
            
            # Recalculate status based on adjusted score
            if recovery_score >= 80:
                recovery_status = "Excellent"
            elif recovery_score >= 60:
                recovery_status = "Good"
            elif recovery_score >= 40:
                recovery_status = "Fair"
            else:
                recovery_status = "Poor"

            ml_predictions = {
                'lifestyle_risk': lifestyle_risk,
                'lifestyle_risk_confidence': round(lifestyle_dict.get('confidence', 0) * 100, 2),
                'recovery_score': recovery_score,
                'recovery_status': recovery_status,
                'exercise_category': exercise_dict.get('category_label', 'Unknown'),
                'exercise_recommendation': exercise_dict.get('recommendation', 'Continue with routine'),
            }
    except Exception as e:
        print(f"DEBUG ML DASHBOARD ERROR: {e}")
        import traceback
        traceback.print_exc()
        ml_predictions = None

    return {
        'profile': profile,
        'recent_data': recent_data,
        'recommendations': recommendations,
        'progress_data': progress_data,
        'progress_assessment': progress_assessment,
        'risk_alerts': risk_alerts,
        'reminders': reminders,
        'disease_predictions': disease_predictions,
        'today_food_entries': today_food_entries,
        'food_by_meal': food_by_meal,
        'today_health_data': today_health_data,
        'today': today,
        'consistency_summary': consistency_summary,
        'drift_alerts': drift_alerts,
        'effort_actions': effort_actions,
        'health_data_list': health_data_list,
        'lifestyle_risks': lifestyle_risks,
        'recovery_today': recovery_today,
        'recovery_yesterday': recovery_yesterday,
        'recovery_7day': recovery_7day,
        'stability_index': stability_index,
        'ml_predictions': ml_predictions,
    }


@login_required
def dashboard_overview(request):
    """Overview dashboard with key metrics and summaries."""
    try:
        context = _build_dashboard_context(request)
    except UserProfile.DoesNotExist:
        return redirect('setup_profile')
    return render(request, 'dashboard_overview.html', context)


@login_required
def dashboard_activity(request):
    """Activity & logging dashboard (health data, trends)."""
    try:
        context = _build_dashboard_context(request)
    except UserProfile.DoesNotExist:
        return redirect('setup_profile')
    return render(request, 'dashboard_activity.html', context)


@login_required
def dashboard_nutrition(request):
    """Nutrition & food tracking dashboard."""
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        return redirect('setup_profile')
    
    # Get selected date from query parameter, default to today
    from datetime import date
    selected_date_str = request.GET.get('date')
    if selected_date_str:
        try:
            selected_date = date.fromisoformat(selected_date_str)
        except (ValueError, TypeError):
            selected_date = date.today()
    else:
        selected_date = date.today()
    
    # Get food entries and health data for selected date
    selected_food_entries = FoodEntry.objects.filter(user=request.user, date=selected_date).order_by('meal_type')
    selected_health_data = HealthData.objects.filter(user=request.user, date=selected_date).first()
    food_by_meal = {
        'breakfast': selected_food_entries.filter(meal_type='breakfast'),
        'lunch': selected_food_entries.filter(meal_type='lunch'),
        'dinner': selected_food_entries.filter(meal_type='dinner'),
        'snacks': selected_food_entries.filter(meal_type='snacks'),
    }
    
    # Get base context
    context = _build_dashboard_context(request)
    # Override with selected date data
    context['today_food_entries'] = selected_food_entries
    context['food_by_meal'] = food_by_meal
    context['today_health_data'] = selected_health_data
    context['today'] = selected_date
    context['selected_date'] = selected_date
    
    return render(request, 'dashboard_nutrition.html', context)


@login_required
def dashboard_alerts(request):
    """Alerts & reminders dashboard."""
    try:
        context = _build_dashboard_context(request)
    except UserProfile.DoesNotExist:
        return redirect('setup_profile')
    return render(request, 'dashboard_alerts.html', context)


@login_required
def dashboard_insights(request):
    """Insights dashboard for consistency, drift, and effort-to-impact."""
    try:
        context = _build_dashboard_context(request)
    except UserProfile.DoesNotExist:
        return redirect('setup_profile')
    return render(request, 'dashboard_insights.html', context)


@login_required
def setup_profile(request):
    """Setup or update user profile"""
    try:
        profile = request.user.userprofile
        is_update = True
    except UserProfile.DoesNotExist:
        profile = None
        is_update = False
    
    if request.method == 'POST':
        if profile:
            # Update existing profile
            profile.age = request.POST.get('age')
            profile.gender = request.POST.get('gender')
            profile.height = request.POST.get('height')
            profile.weight = request.POST.get('weight')
            profile.activity_level = request.POST.get('activity_level')
            profile.health_goal = request.POST.get('health_goal')
            profile.dietary_preference = request.POST.get('dietary_preference')
            profile.allergies = request.POST.get('allergies', '')
            profile.medical_conditions = request.POST.get('medical_conditions', '')
            profile.save()
            messages.success(request, 'Profile updated successfully!')
        else:
            # Create new profile
            profile = UserProfile.objects.create(
                user=request.user,
                age=request.POST.get('age'),
                gender=request.POST.get('gender'),
                height=request.POST.get('height'),
                weight=request.POST.get('weight'),
                activity_level=request.POST.get('activity_level'),
                health_goal=request.POST.get('health_goal'),
                dietary_preference=request.POST.get('dietary_preference'),
                allergies=request.POST.get('allergies', ''),
                medical_conditions=request.POST.get('medical_conditions', ''),
            )
            messages.success(request, 'Profile created successfully!')
        
        return redirect('dashboard')
    
    context = {
        'profile': profile,
        'is_update': is_update,
    }
    return render(request, 'setup_profile.html', context)


@login_required
def recommendations(request):
    """View and generate recommendations"""
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        messages.warning(request, 'Please complete your profile first.')
        return redirect('setup_profile')
    
    return render(request, 'recommendations.html', {})


@login_required
def diet_recommendation(request):
    """Diet recommendation page"""
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        messages.warning(request, 'Please complete your profile first.')
        return redirect('setup_profile')
    
    if request.method == 'POST':
        # Generate new recommendation
        data = generate_diet_recommendation(profile)
        title = f"Diet Plan - {data['calories']} calories/day"
        description = f"Personalized diet plan with {data['macronutrients']['protein_percent']}% protein, {data['macronutrients']['carbs_percent']}% carbs, {data['macronutrients']['fats_percent']}% fats"
        
        # Deactivate old recommendations
        Recommendation.objects.filter(user=request.user, recommendation_type='diet', is_active=True).update(is_active=False)
        
        # Create new recommendation
        Recommendation.objects.create(
            user=request.user,
            recommendation_type='diet',
            title=title,
            description=description,
            details=data,
            is_active=True
        )
        messages.success(request, 'New diet plan generated successfully!')
        return redirect('diet_recommendation')
    
    # Get active recommendation
    recommendation = Recommendation.objects.filter(user=request.user, recommendation_type='diet', is_active=True).first()
    
    return render(request, 'recommendation_diet.html', {
        'recommendation': recommendation,
        'profile': profile
    })


@login_required
def exercise_recommendation(request):
    """Exercise recommendation page"""
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        messages.warning(request, 'Please complete your profile first.')
        return redirect('setup_profile')
    
    if request.method == 'POST':
        # Generate new recommendation
        data = generate_exercise_recommendation(profile)
        title = f"Exercise Plan - {data['fitness_level'].title()} Level"
        description = f"{data['exercise_type'].title()} workout plan, {data['frequency']}"
        
        # Deactivate old recommendations
        Recommendation.objects.filter(user=request.user, recommendation_type='exercise', is_active=True).update(is_active=False)
        
        # Create new recommendation
        Recommendation.objects.create(
            user=request.user,
            recommendation_type='exercise',
            title=title,
            description=description,
            details=data,
            is_active=True
        )
        messages.success(request, 'New exercise plan generated successfully!')
        return redirect('exercise_recommendation')
    
    # Get active recommendation
    recommendation = Recommendation.objects.filter(user=request.user, recommendation_type='exercise', is_active=True).first()
    
    return render(request, 'recommendation_exercise.html', {
        'recommendation': recommendation,
        'profile': profile
    })


@login_required
def sleep_recommendation(request):
    """Sleep recommendation page"""
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        messages.warning(request, 'Please complete your profile first.')
        return redirect('setup_profile')
    
    if request.method == 'POST':
        # Generate new recommendation
        # Get average exercise minutes from recent data
        recent_data = HealthData.objects.filter(user=request.user).order_by('-date').first()
        exercise_minutes = recent_data.exercise_minutes if recent_data and recent_data.exercise_minutes else 0
        
        data = generate_sleep_recommendation(profile, exercise_minutes)
        title = f"Sleep Plan - {data['sleep_hours']} hours"
        description = f"Optimal sleep schedule: {data['schedule']['bedtime']} to {data['schedule']['wake_time']}"
        
        # Deactivate old recommendations
        Recommendation.objects.filter(user=request.user, recommendation_type='sleep', is_active=True).update(is_active=False)
        
        # Create new recommendation
        Recommendation.objects.create(
            user=request.user,
            recommendation_type='sleep',
            title=title,
            description=description,
            details=data,
            is_active=True
        )
        messages.success(request, 'New sleep plan generated successfully!')
        return redirect('sleep_recommendation')
    
    # Get active recommendation
    recommendation = Recommendation.objects.filter(user=request.user, recommendation_type='sleep', is_active=True).first()
    
    return render(request, 'recommendation_sleep.html', {
        'recommendation': recommendation,
        'profile': profile
    })


@login_required
@require_http_methods(["POST"])
def generate_recommendation(request):
    """Generate new recommendation via AJAX"""
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        return JsonResponse({'error': 'Profile not found'}, status=400)
    
    rec_type = request.POST.get('type')
    
    if rec_type == 'diet':
        data = generate_diet_recommendation(profile)
        title = f"Diet Plan - {data['calories']} calories/day"
        description = f"Personalized diet plan with {data['macronutrients']['protein_percent']}% protein, {data['macronutrients']['carbs_percent']}% carbs, {data['macronutrients']['fats_percent']}% fats"
        
    elif rec_type == 'exercise':
        data = generate_exercise_recommendation(profile)
        title = f"Exercise Plan - {data['fitness_level'].title()} Level"
        description = f"{data['exercise_type'].title()} workout plan, {data['frequency']}"
        
    elif rec_type == 'sleep':
        # Get average exercise minutes from recent data
        recent_data = HealthData.objects.filter(user=request.user).order_by('-date').first()
        exercise_minutes = recent_data.exercise_minutes if recent_data and recent_data.exercise_minutes else 0
        
        data = generate_sleep_recommendation(profile, exercise_minutes)
        title = f"Sleep Plan - {data['sleep_hours']} hours"
        description = f"Optimal sleep schedule: {data['schedule']['bedtime']} to {data['schedule']['wake_time']}"
        
    else:
        return JsonResponse({'error': 'Invalid recommendation type'}, status=400)
    
    # Deactivate old recommendations of this type
    Recommendation.objects.filter(user=request.user, recommendation_type=rec_type, is_active=True).update(is_active=False)
    
    # Create new recommendation
    recommendation = Recommendation.objects.create(
        user=request.user,
        recommendation_type=rec_type,
        title=title,
        description=description,
        details=data,
        is_active=True
    )
    
    return JsonResponse({
        'success': True,
        'recommendation': {
            'id': recommendation.id,
            'type': recommendation.recommendation_type,
            'title': recommendation.title,
            'description': recommendation.description,
            'details': recommendation.details,
        }
    })


@login_required
@require_http_methods(["POST"])
def add_health_data(request):
    """Add health data entry"""
    try:
        from datetime import date, timedelta
        
        weight = float(request.POST.get('weight'))
        sleep_hours = request.POST.get('sleep_hours')
        exercise_minutes = request.POST.get('exercise_minutes')
        calories_consumed = request.POST.get('calories_consumed')
        water_intake = request.POST.get('water_intake_liters')
        stress_level = request.POST.get('stress_level')
        daily_steps = request.POST.get('daily_steps')
        notes = request.POST.get('notes', '')
        
        # Feature: Automatically increment the date to the next day for rapid testing 
        # so multiple submissions don't pile up on the same day.
        latest_entry = HealthData.objects.filter(user=request.user).order_by('-date').first()
        if latest_entry:
            # Add one day to the most recent entry's date
            entry_date = latest_entry.date + timedelta(days=1)
        else:
            entry_date = date.today()
        
        health_data = HealthData.objects.create(
            user=request.user,
            date=entry_date,
            weight=weight,
            sleep_hours=float(sleep_hours) if sleep_hours else None,
            exercise_minutes=int(exercise_minutes) if exercise_minutes else None,
            calories_consumed=float(calories_consumed) if calories_consumed else None,
            water_intake_liters=float(water_intake) if water_intake else None,
            stress_level=int(stress_level) if stress_level else None,
            daily_steps=int(daily_steps) if daily_steps else None,
            notes=notes,
        )
        
        # Update nutrition totals from food entries for this date
        update_nutrition_totals(request.user, entry_date)
        
        # Execute ML predictions on the newly saved data
        ml_predictions = None
        try:
            from ml_models.predict_models import (
                predict_lifestyle_risk,
                predict_recovery_score,
                predict_exercise_category,
            )
            age = request.user.userprofile.age
            sleep_hours_val = health_data.sleep_hours or 7.0
            activity_level_val = health_data.exercise_minutes or 30
            stress_level_val = health_data.stress_level or 5
            daily_steps_val = health_data.daily_steps or 5000

            tdee_val = getattr(request.user.userprofile, 'tdee', None) or 2000
            calories_consumed_val = (
                health_data.calories_consumed 
                if health_data.calories_consumed is not None 
                else health_data.total_calories if health_data.total_calories > 0 else tdee_val
            )
            bmi_val = request.user.userprofile.bmi

            ml_predictions = {
                'lifestyle_risk': predict_lifestyle_risk(
                    bmi_val, age, sleep_hours_val, activity_level_val,
                    stress_level_val, daily_steps_val
                ),
                'recovery_score': predict_recovery_score(
                    sleep_hours_val, activity_level_val,
                    calories_consumed_val, stress_level_val
                ),
                'exercise_category': predict_exercise_category(
                    bmi_val, age, sleep_hours_val, activity_level_val,
                    stress_level_val, daily_steps_val
                ),
            }
            if 'confidence' in ml_predictions['lifestyle_risk']:
                ml_predictions['lifestyle_risk']['confidence'] = round(
                    ml_predictions['lifestyle_risk']['confidence'] * 100, 2
                )
        except Exception as ml_err:
            print("ML prediction error during save:", ml_err)
        
        return JsonResponse({
            'success': True,
            'data': {
                'id': health_data.id,
                'date': health_data.date.isoformat(),
                'weight': health_data.weight,
                'sleep_hours': health_data.sleep_hours,
                'exercise_minutes': health_data.exercise_minutes,
                'calories_consumed': health_data.calories_consumed,
                'water_intake_liters': health_data.water_intake_liters,
                'stress_level': health_data.stress_level,
                'daily_steps': health_data.daily_steps,
            },
            'ml_predictions': ml_predictions
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


def update_nutrition_totals(user, date):
    """Update nutrition totals in HealthData based on food entries"""
    food_entries = FoodEntry.objects.filter(user=user, date=date)
    
    totals = {
        'total_calories': 0,
        'total_protein': 0,
        'total_carbs': 0,
        'total_fats': 0,
        'total_fiber': 0,
    }
    
    for entry in food_entries:
        totals['total_calories'] += entry.total_calories
        totals['total_protein'] += entry.total_protein
        totals['total_carbs'] += entry.total_carbs
        totals['total_fats'] += entry.total_fats
        totals['total_fiber'] += entry.total_fiber
    
    # Update or create HealthData entry
    health_data = HealthData.objects.filter(user=user, date=date).first()
    if health_data:
        health_data.total_calories = round(totals['total_calories'], 2)
        health_data.total_protein = round(totals['total_protein'], 2)
        health_data.total_carbs = round(totals['total_carbs'], 2)
        health_data.total_fats = round(totals['total_fats'], 2)
        health_data.total_fiber = round(totals['total_fiber'], 2)
        health_data.save()


@login_required
@require_http_methods(["POST"])
def add_food_entry(request):
    """Add a food entry for a meal"""
    try:
        from datetime import date as date_obj
        
        food_name = request.POST.get('food_name')
        meal_type = request.POST.get('meal_type')
        quantity = float(request.POST.get('quantity', 1.0))
        unit = request.POST.get('unit', 'serving')
        entry_date_str = request.POST.get('date')
        
        if entry_date_str:
            entry_date = date_obj.fromisoformat(entry_date_str)
        else:
            # Get last entry date or use today
            last_entry = HealthData.objects.filter(user=request.user).order_by('-date').first()
            entry_date = last_entry.date if last_entry else date_obj.today()
        
        # Calculate nutrition
        nutrition = calculate_nutrition(food_name, quantity, unit)
        if not nutrition:
            return JsonResponse({'error': f'Food "{food_name}" not found in database'}, status=400)
        
        # Get or create health data for this date
        health_data = HealthData.objects.filter(user=request.user, date=entry_date).first()
        if not health_data:
            # Create minimal health data entry
            health_data = HealthData.objects.create(
                user=request.user,
                date=entry_date,
                weight=request.user.userprofile.weight,  # Use current weight
            )
        
        # Get food info to calculate per-unit values
        from .food_database import get_food_info
        food_info = get_food_info(food_name)
        if not food_info:
            return JsonResponse({'error': f'Food "{food_name}" not found in database'}, status=400)
        
        # Calculate per-unit values based on unit type
        if unit == 'serving' or unit == 'servings':
            # Per serving = per 100g * (serving_size / 100)
            serving_multiplier = food_info['serving_size'] / 100.0
            calories_per_unit = food_info['calories_per_100g'] * serving_multiplier
            protein_per_unit = food_info['protein_per_100g'] * serving_multiplier
            carbs_per_unit = food_info['carbs_per_100g'] * serving_multiplier
            fats_per_unit = food_info['fats_per_100g'] * serving_multiplier
            fiber_per_unit = food_info['fiber_per_100g'] * serving_multiplier
        else:  # gram
            # Per gram = per 100g / 100
            calories_per_unit = food_info['calories_per_100g'] / 100.0
            protein_per_unit = food_info['protein_per_100g'] / 100.0
            carbs_per_unit = food_info['carbs_per_100g'] / 100.0
            fats_per_unit = food_info['fats_per_100g'] / 100.0
            fiber_per_unit = food_info['fiber_per_100g'] / 100.0
        
        # Create food entry
        food_entry = FoodEntry.objects.create(
            user=request.user,
            health_data=health_data,
            date=entry_date,
            meal_type=meal_type,
            food_name=food_name,
            quantity=quantity,
            unit=unit,
            calories_per_unit=round(calories_per_unit, 2),
            protein_per_unit=round(protein_per_unit, 2),
            carbs_per_unit=round(carbs_per_unit, 2),
            fats_per_unit=round(fats_per_unit, 2),
            fiber_per_unit=round(fiber_per_unit, 2),
        )
        
        # Update nutrition totals
        update_nutrition_totals(request.user, entry_date)
        
        return JsonResponse({
            'success': True,
            'food_entry': {
                'id': food_entry.id,
                'food_name': food_entry.food_name,
                'meal_type': food_entry.meal_type,
                'quantity': food_entry.quantity,
                'total_calories': food_entry.total_calories,
                'total_protein': food_entry.total_protein,
                'total_carbs': food_entry.total_carbs,
                'total_fats': food_entry.total_fats,
                'total_fiber': food_entry.total_fiber,
            }
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def delete_food_entry(request, entry_id):
    """Delete a food entry"""
    try:
        food_entry = FoodEntry.objects.get(id=entry_id, user=request.user)
        entry_date = food_entry.date
        food_entry.delete()
        
        # Update nutrition totals
        update_nutrition_totals(request.user, entry_date)
        
        return JsonResponse({'success': True, 'message': 'Food entry deleted successfully'})
    except FoodEntry.DoesNotExist:
        return JsonResponse({'error': 'Food entry not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def get_food_suggestions_view(request):
    """Get food suggestions for a meal type"""
    meal_type = request.GET.get('meal_type', 'breakfast')
    try:
        profile = request.user.userprofile
        dietary_preference = profile.dietary_preference
    except:
        dietary_preference = 'none'
    
    suggestions = get_food_suggestions(meal_type, dietary_preference)
    
    return JsonResponse({
        'success': True,
        'suggestions': suggestions
    })


@login_required
def get_food_replacements_view(request):
    """Get healthier food alternatives for a given food (Food Replacement Engine)"""
    food = request.GET.get('food', '').strip()
    if not food:
        return JsonResponse({'success': False, 'error': 'Please enter a food name'}, status=400)
    alternatives = get_food_replacements(food)
    return JsonResponse({
        'success': True,
        'query': food,
        'alternatives': alternatives,
    })


def register_view(request):
    """User registration"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        
        if password != password2:
            messages.error(request, 'Passwords do not match')
            return render(request, 'register.html')
        
        if len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters')
            return render(request, 'register.html')
        
        from django.contrib.auth.models import User
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'register.html')
        
        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)
        messages.success(request, 'Registration successful! Please complete your profile.')
        return redirect('setup_profile')
    
    return render(request, 'register.html')


def login_view(request):
    """User login"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'login.html')


@login_required
def analytics(request):
    """Advanced analytics page with new features"""
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        messages.warning(request, 'Please complete your profile first.')
        return redirect('setup_profile')
    
    # Get health data count specifically for the hub check
    health_data_count = HealthData.objects.filter(user=request.user).count()
    
    context = {
        'profile': profile,
        'has_sufficient_data': health_data_count >= 1,
    }
    
    return render(request, 'analytics.html', context)


@login_required
def analytics_recovery(request):
    """Recovery and stability analysis page"""
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        messages.warning(request, 'Please complete your profile first.')
        return redirect('setup_profile')
        
    health_data_list = list(HealthData.objects.filter(user=request.user).order_by('date'))
    has_sufficient_data = len(health_data_list) >= 1

    records = HealthData.objects.filter(user=request.user).order_by('-date')
    today_data = records[0] if records.count() > 0 else None
    yesterday_data = records[1] if records.count() > 1 else None
    recovery_today = calculate_recovery_score(today_data, profile)
    recovery_yesterday = calculate_recovery_score(yesterday_data, profile)
    stability_index = compute_stability_index(health_data_list)
    
    if request.method == 'POST':
        if not has_sufficient_data:
            messages.error(request, 'Not enough data for analysis.')
            return redirect('analytics_recovery')

        analysis_data = generate_recovery_stability_analysis(profile, health_data_list)
        
        # Save to database
        RecoveryStabilityAnalysis.objects.create(
            user=request.user,
            recovery_days=analysis_data['recovery_days'],
            stability_score=analysis_data['stability_score'],
            is_stable=analysis_data['is_stable'],
            risk_level=analysis_data['risk_level'],
            consistency_score=analysis_data['consistency_score'],
            adherence_rate=analysis_data['adherence_rate'],
            streak_days=analysis_data['streak_days'],
            recommendations=analysis_data['recommendations'],
        )
        messages.success(request, 'Recovery analysis generated successfully!')
        return redirect('analytics_recovery')
    
    recovery_analysis = RecoveryStabilityAnalysis.objects.filter(user=request.user).order_by('-created_at').first()
    
    return render(request, 'analytics_recovery.html', {
        'recovery_analysis': recovery_analysis,
        'has_sufficient_data': has_sufficient_data,
        'recovery_today': recovery_today,
        'recovery_yesterday': recovery_yesterday,
        'stability_index': stability_index,
    })


@login_required
def analytics_habit_streak(request):
    """Habit Streak Tracker: current streaks for sleep, exercise, diet, and overall activity."""
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        messages.warning(request, 'Please complete your profile first.')
        return redirect('setup_profile')

    entries = list(HealthData.objects.filter(user=request.user).order_by('-date'))

    def _current_streak(predicate):
        """Return current consecutive-day streak from most recent entry."""
        if not entries:
            return 0
        from datetime import timedelta
        first = entries[0]
        if not predicate(first):
            return 0
        streak = 1
        prev_date = first.date
        for entry in entries[1:]:
            # Require calendar-consecutive dates for the streak
            if (prev_date - entry.date) != timedelta(days=1):
                break
            if predicate(entry):
                streak += 1
                prev_date = entry.date
            else:
                break
        return streak

    sleep_streak = _current_streak(
        lambda e: e.sleep_hours is not None and e.sleep_hours >= 7.0
    )
    exercise_streak = _current_streak(
        lambda e: e.exercise_minutes is not None and e.exercise_minutes >= 30
    )
    # Diet streak assumes TDEE is met. We can fetch tdee inside lambda if needed, but easier to use baseline ~2000
    tdee = getattr(profile, 'tdee', None) or 2000
    diet_streak = _current_streak(
        lambda e: (
            (e.total_calories is not None and abs(e.total_calories - tdee) <= 300) or
            (e.calories_consumed is not None and abs(e.calories_consumed - tdee) <= 300)
        )
    )
    # Overall Activity Streak means ANY of the healthy thresholds was met
    activity_streak = _current_streak(
        lambda e: any([
            (e.sleep_hours or 0) >= 7.0,
            (e.exercise_minutes or 0) >= 30,
            (e.water_intake_liters or 0) >= 2.0
        ])
    )

    context = {
        'profile': profile,
        'has_data': bool(entries),
        'sleep_streak': sleep_streak,
        'exercise_streak': exercise_streak,
        'diet_streak': diet_streak,
        'activity_streak': activity_streak,
        'latest_date': entries[0].date if entries else None,
    }
    return render(request, 'analytics_habit_streak.html', context)


@login_required
def analytics_risk_momentum(request):
    """Health Risk Momentum Tracker based on lifestyle risk trends."""
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        messages.warning(request, 'Please complete your profile first.')
        return redirect('setup_profile')

    # Get recent health data, calculate daily risk
    health_data_list = list(HealthData.objects.filter(user=request.user).order_by('date'))
    # Use last 14-30 days for momentum
    window = health_data_list[-30:] 
    
    momentum = []
    if len(window) >= 2:
        # Calculate daily risk score using the central formula
        daily_risks = []
        for d in window:
            risk_dict = calculate_health_risk(profile, [d])
            daily_risks.append({
                'date': d.date,
                'score': risk_dict['risk_score']
            })
            
        first = daily_risks[0]
        last = daily_risks[-1]
        days = max(1, (last['date'] - first['date']).days)
        weeks = max(1.0, days / 7.0)
        change_per_week = (last['score'] - first['score']) / weeks
        
        direction = 'increasing' if change_per_week > 0 else 'decreasing' if change_per_week < 0 else 'stable'
        
        momentum.append({
            'disease': 'Overall Lifestyle Risk',
            'change_per_week': round(change_per_week, 2),
            'abs_change_per_week': abs(round(change_per_week, 2)),
            'direction': direction,
            'start_score': first['score'],
            'end_score': last['score'],
            'weeks_span': round(weeks, 1),
        })
        
        primary_disease = 'Overall Lifestyle Risk'
        primary_momentum = momentum[0]
        
        labels = [r['date'].strftime('%Y-%m-%d') for r in daily_risks]
        values = [r['score'] for r in daily_risks]
        
        import json
        primary_series_labels = json.dumps(labels)
        primary_series_values = json.dumps(values)
    else:
        primary_disease = None
        primary_momentum = None
        primary_series_labels = '[]'
        primary_series_values = '[]'

    return render(request, 'analytics_risk_momentum.html', {
        'momentum': momentum,
        'primary_disease': primary_disease,
        'primary_momentum': primary_momentum,
        'primary_series_labels': primary_series_labels,
        'primary_series_values': primary_series_values,
    })


@login_required
def analytics_biological_age(request):
    """Biological Age Estimator analytics page."""
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        messages.warning(request, 'Please complete your profile first.')
        return redirect('setup_profile')

    health_data_list = list(HealthData.objects.filter(user=request.user).order_by('date'))
    has_sufficient_data = len(health_data_list) >= 1

    from datetime import date
    today = date.today()
    today_data = HealthData.objects.filter(user=request.user, date=today).first()
    recovery_today = calculate_recovery_score(today_data, profile) if today_data else None

    consistency_summary = calculate_consistency_score(health_data_list) if health_data_list else None
    stability_index = compute_stability_index(health_data_list) if health_data_list else None

    bio = estimate_biological_age(
        profile,
        health_data_list,
        consistency_summary=consistency_summary,
        stability_index=stability_index,
        recovery_today=recovery_today,
    )

    return render(request, 'analytics_biological_age.html', {
        'has_sufficient_data': has_sufficient_data,
        'bio': bio,
        'consistency_summary': consistency_summary,
        'stability_index': stability_index,
        'recovery_today': recovery_today,
    })


@login_required
def analytics_health_balance(request):
    """Health Balance Radar analytics page."""
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        messages.warning(request, 'Please complete your profile first.')
        return redirect('setup_profile')

    health_data_list = list(HealthData.objects.filter(user=request.user).order_by('date'))
    has_sufficient_data = len(health_data_list) >= 1

    from datetime import date
    today = date.today()
    today_data = HealthData.objects.filter(user=request.user, date=today).first()
    recovery_today = calculate_recovery_score(today_data, profile) if today_data else None
    stability_index = compute_stability_index(health_data_list) if health_data_list else None

    balance = compute_health_balance_dimensions(
        profile,
        health_data_list,
        recovery_today=recovery_today,
        stability_index=stability_index,
    )

    radar_labels = ['Sleep', 'Exercise', 'Calories', 'Stress', 'Hydration']
    radar_values = [
        balance['sleep'],
        balance['exercise'],
        balance['calories'],
        balance['stress'],
        balance['hydration'],
    ]

    return render(request, 'analytics_health_balance.html', {
        'has_sufficient_data': has_sufficient_data,
        'balance': balance,
        'radar_labels': json.dumps(radar_labels),
        'radar_values': json.dumps(radar_values),
    })

@login_required
def analytics_correlation(request):
    """Correlation analysis page"""
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        messages.warning(request, 'Please complete your profile first.')
        return redirect('setup_profile')
        
    # Fetch the last 30 entries for analysis, ordered by date ascending for sequential analysis
    health_data_list = list(HealthData.objects.filter(user=request.user).order_by('-date')[:30])
    health_data_list.reverse() # Reverse to chronological order for pandas analysis
    
    has_sufficient_data = len(health_data_list) >= 1
    
    if request.method == 'POST':
        if not has_sufficient_data:
            messages.error(request, 'Not enough data for analysis.')
            return redirect('analytics_correlation')

        tdee = getattr(profile, 'tdee', None)
        analysis_data = generate_correlation_analysis(health_data_list, tdee=tdee)

        # Save to database
        BehaviorCorrelationAnalysis.objects.create(
            user=request.user,
            insights=analysis_data['insights'],
            correlations=analysis_data['correlations'],
            root_causes=analysis_data['root_causes'],
            data_points_analyzed=analysis_data['data_points'],
        )
        messages.success(request, 'Correlation analysis generated successfully!')
        return redirect('analytics_correlation')

    correlation_analysis = BehaviorCorrelationAnalysis.objects.filter(user=request.user).order_by('-created_at').first()

    return render(request, 'analytics_correlation.html', {
        'correlation_analysis': correlation_analysis,
        'has_sufficient_data': has_sufficient_data
    })


@login_required
def analytics_habits(request):
    """Habit analysis page"""
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        messages.warning(request, 'Please complete your profile first.')
        return redirect('setup_profile')
        
    health_data_list = list(HealthData.objects.filter(user=request.user).order_by('date'))
    has_sufficient_data = len(health_data_list) >= 1
    
    if request.method == 'POST':
        if not has_sufficient_data:
            messages.error(request, 'Not enough data for analysis.')
            return redirect('analytics_habits')

        analysis_data = generate_habit_sensitivity_analysis(profile, health_data_list)
        analysis_data['total_habits'] = analysis_data.get('total_habits', len(analysis_data.get('habits', [])))
        
        # Save to database
        HabitSensitivityAnalysis.objects.create(
            user=request.user,
            fragile_habits=analysis_data['fragile_habits'],
            resilient_habits=analysis_data['resilient_habits'],
            high_impact_habits=analysis_data['high_impact_habits'],
            total_habits_analyzed = analysis_data.get('total_habits_analyzed', 0)
        )
        messages.success(request, 'Habit analysis generated successfully!')
        return redirect('analytics_habits')
    
    habit_analysis = HabitSensitivityAnalysis.objects.filter(user=request.user).order_by('-created_at').first()
    
    return render(request, 'analytics_habits.html', {
        'habit_analysis': habit_analysis,
        'has_sufficient_data': has_sufficient_data
    })


@login_required
def simulator(request):
    """What-If Health Simulator page"""
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        messages.warning(request, 'Please complete your profile first.')
        return redirect('setup_profile')
    
    # Get current health data averages
    health_data_list = list(HealthData.objects.filter(user=request.user).order_by('date'))
    
    # Calculate current averages
    if health_data_list:
        current_sleep = sum([d.sleep_hours for d in health_data_list if d.sleep_hours]) / len([d for d in health_data_list if d.sleep_hours]) if any(d.sleep_hours for d in health_data_list) else 7
        current_exercise = sum([d.exercise_minutes for d in health_data_list if d.exercise_minutes]) / len([d for d in health_data_list if d.exercise_minutes]) if any(d.exercise_minutes for d in health_data_list) else 0
        current_weight = health_data_list[-1].weight if health_data_list else profile.weight
    else:
        current_sleep = 7
        current_exercise = 0
        current_weight = profile.weight
    
    context = {
        'profile': profile,
        'current_sleep': round(current_sleep, 1),
        'current_exercise': round(current_exercise, 0),
        'current_weight': current_weight,
        'current_bmi': profile.bmi,
    }
    
    return render(request, 'simulator.html', context)


@login_required
@require_http_methods(["POST"])
def run_simulation(request):
    """Run health simulation based on what-if scenario"""
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Profile not found'}, status=400)
    
    try:
        data = json.loads(request.body)
        new_sleep = float(data.get('sleep_hours', 7))
        new_exercise = float(data.get('exercise_minutes', 0))
        days = int(data.get('days', 14))
        
        # Get current health data
        health_data_list = list(HealthData.objects.filter(user=request.user).order_by('date'))
        
        if health_data_list:
            current_sleep = sum([d.sleep_hours for d in health_data_list if d.sleep_hours]) / len([d for d in health_data_list if d.sleep_hours]) if any(d.sleep_hours for d in health_data_list) else 7
            current_exercise = sum([d.exercise_minutes for d in health_data_list if d.exercise_minutes]) / len([d for d in health_data_list if d.exercise_minutes]) if any(d.exercise_minutes for d in health_data_list) else 0
            current_weight = health_data_list[-1].weight
        else:
            current_sleep = 7
            current_exercise = 0
            current_weight = profile.weight
        
        # Run simulation
        simulator_model = HealthSimulatorModel()
        results = simulator_model.simulate_scenario(
            current_weight=current_weight,
            current_sleep=current_sleep,
            current_exercise=current_exercise,
            new_sleep=new_sleep,
            new_exercise=new_exercise,
            days=days,
            age=profile.age,
            bmi=profile.bmi,
            activity_level=profile.activity_level
        )
        
        return JsonResponse({
            'success': True,
            'results': results
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def generate_recovery_analysis(request):
    """Generate recovery and stability analysis"""
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        return JsonResponse({'error': 'Profile not found'}, status=400)
    
    health_data_list = list(HealthData.objects.filter(user=request.user).order_by('date'))
    
    if len(health_data_list) < 1:
        return JsonResponse({'error': 'Add at least 1 data point for analysis'}, status=400)
    
    analysis_data = generate_recovery_stability_analysis(profile, health_data_list)
    
    # Save to database
    analysis = RecoveryStabilityAnalysis.objects.create(
        user=request.user,
        recovery_days=analysis_data['recovery_days'],
        stability_score=analysis_data['stability_score'],
        is_stable=analysis_data['is_stable'],
        risk_level=analysis_data['risk_level'],
        consistency_score=analysis_data['consistency_score'],
        adherence_rate=analysis_data['adherence_rate'],
        streak_days=analysis_data['streak_days'],
        recommendations=analysis_data['recommendations'],
    )
    
    return JsonResponse({
        'success': True,
        'analysis': {
            'recovery_days': analysis.recovery_days,
            'stability_score': analysis.stability_score,
            'is_stable': analysis.is_stable,
            'risk_level': analysis.risk_level,
            'consistency_score': analysis.consistency_score,
            'adherence_rate': analysis.adherence_rate,
            'streak_days': analysis.streak_days,
            'recommendations': analysis.recommendations,
        }
    })


@login_required
@require_http_methods(["POST"])
def generate_correlation_analysis_view(request):
    """Generate behavior-cause correlation analysis"""
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        return JsonResponse({'error': 'Profile not found'}, status=400)
    
    # Fetch the last 30 entries for analysis, ordered by date ascending for sequential analysis
    health_data_list = list(HealthData.objects.filter(user=request.user).order_by('-date')[:30])
    health_data_list.reverse() # Reverse to chronological order for pandas analysis
    
    if len(health_data_list) < 1:
        return JsonResponse({'error': 'Add at least 1 data point for analysis'}, status=400)

    tdee = getattr(profile, 'tdee', None)
    analysis_data = generate_correlation_analysis(health_data_list, tdee=tdee)

    # Save to database
    analysis = BehaviorCorrelationAnalysis.objects.create(
        user=request.user,
        insights=analysis_data['insights'],
        correlations=analysis_data['correlations'],
        root_causes=analysis_data['root_causes'],
        data_points_analyzed=analysis_data['data_points'],
    )
    
    return JsonResponse({
        'success': True,
        'analysis': {
            'insights': analysis.insights,
            'correlations': analysis.correlations,
            'root_causes': analysis.root_causes,
            'data_points': analysis.data_points_analyzed,
        }
    })


@login_required
@require_http_methods(["POST"])
def generate_habit_analysis(request):
    """Generate habit sensitivity analysis"""
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        return JsonResponse({'error': 'Profile not found'}, status=400)
    
    health_data_list = list(HealthData.objects.filter(user=request.user).order_by('date'))
    
    if len(health_data_list) < 1:
        return JsonResponse({'error': 'Add at least 1 data point for analysis'}, status=400)
    
    analysis_data = generate_habit_sensitivity_analysis(profile, health_data_list)
    
    # Save to database
    analysis = HabitSensitivityAnalysis.objects.create(
        user=request.user,
        habits=analysis_data['habits'],
        fragile_habits=analysis_data['fragile_habits'],
        resilient_habits=analysis_data['resilient_habits'],
        high_impact_habits=analysis_data['high_impact_habits'],
        total_habits_analyzed=analysis_data.get('total_habits', 0),
    )
    
    return JsonResponse({
        'success': True,
        'analysis': {
            'habits': analysis.habits,
            'fragile_habits': analysis.fragile_habits,
            'resilient_habits': analysis.resilient_habits,
            'high_impact_habits': analysis.high_impact_habits,
            'total_habits': analysis.total_habits_analyzed,
        }
    })


@login_required
@require_http_methods(["POST"])
def delete_health_data(request, data_id):
    """Delete health data entry"""
    try:
        health_data = HealthData.objects.get(id=data_id, user=request.user)
        health_data.delete()
        return JsonResponse({'success': True, 'message': 'Health data deleted successfully'})
    except HealthData.DoesNotExist:
        return JsonResponse({'error': 'Health data not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def create_reminder(request):
    """Create a new reminder"""
    try:
        time_str = request.POST.get('time')
        if isinstance(time_str, str):
            reminder_time = datetime.strptime(time_str, '%H:%M').time()
        else:
            reminder_time = time_str

        reminder = Reminder.objects.create(
            user=request.user,
            reminder_type=request.POST.get('reminder_type'),
            time=reminder_time,
            message=request.POST.get('message', ''),
            days_of_week=request.POST.getlist('days_of_week') or list(range(7)),
        )

        if hasattr(reminder.time, 'strftime'):
            formatted_time = reminder.time.strftime('%H:%M')
        else:
            formatted_time = str(reminder.time)

        return JsonResponse({
            'success': True,
            'reminder': {
                'id': reminder.id,
                'type': reminder.reminder_type,
                'time': formatted_time,
                'message': reminder.message,
            }
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def toggle_reminder(request, reminder_id):
    """Toggle reminder active status"""
    try:
        reminder = Reminder.objects.get(id=reminder_id, user=request.user)
        reminder.is_active = not reminder.is_active
        reminder.save()
        return JsonResponse({'success': True, 'is_active': reminder.is_active})
    except Reminder.DoesNotExist:
        return JsonResponse({'error': 'Reminder not found'}, status=404)


@login_required
@require_http_methods(["POST"])
def delete_reminder(request, reminder_id):
    """Delete a reminder"""
    try:
        reminder = Reminder.objects.get(id=reminder_id, user=request.user)
        reminder.delete()
        return JsonResponse({'success': True})
    except Reminder.DoesNotExist:
        return JsonResponse({'error': 'Reminder not found'}, status=404)


@login_required
@require_http_methods(["POST"])
def mark_alert_read(request, alert_id):
    """Mark risk alert as read"""
    try:
        alert = HealthRiskAlert.objects.get(id=alert_id, user=request.user)
        alert.is_read = True
        alert.save()
        return JsonResponse({'success': True})
    except HealthRiskAlert.DoesNotExist:
        return JsonResponse({'error': 'Alert not found'}, status=404)


@login_required
@require_http_methods(["POST"])
def generate_disease_prediction(request):
    """Generate disease risk predictions"""
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        return JsonResponse({'error': 'Profile not found'}, status=400)
    
    health_data_list = list(HealthData.objects.filter(user=request.user).order_by('date'))
    
    if len(health_data_list) < 1:
        return JsonResponse({'error': 'Add at least 1 data point for prediction'}, status=400)
    
    predictions = predict_disease_risks(profile, health_data_list)
    
    # Save predictions to database
    saved_predictions = []
    for disease, data in predictions.items():
        if data['risk_score'] > 20:  # Only save if risk is significant
            prediction = DiseasePrediction.objects.create(
                user=request.user,
                disease_type=disease.replace('_', ' ').title(),
                risk_score=data['risk_score'],
                risk_level=data['risk_level'],
                factors=data['factors'],
                recommendations=data['recommendations']
            )
            saved_predictions.append({
                'disease': prediction.disease_type,
                'risk_score': prediction.risk_score,
                'risk_level': prediction.risk_level,
                'factors': prediction.factors,
                'recommendations': prediction.recommendations,
            })
    
    return JsonResponse({
        'success': True,
        'predictions': saved_predictions
    })

