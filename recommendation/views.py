from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json

from .models import UserProfile, HealthData, Recommendation, RecoveryStabilityAnalysis, BehaviorCorrelationAnalysis, HabitSensitivityAnalysis, Reminder, HealthRiskAlert, DiseasePrediction, FoodEntry
from .food_database import calculate_nutrition, get_food_suggestions, get_food_replacements
from .utils import (
    generate_diet_recommendation, generate_exercise_recommendation, generate_sleep_recommendation,
    generate_recovery_stability_analysis, generate_correlation_analysis, generate_habit_sensitivity_analysis,
    assess_progress, assess_health_risks, predict_disease_risks, calculate_consistency_score,
    detect_health_drift, suggest_effort_to_impact_actions, compute_lifestyle_risk_predictions,
    calculate_recovery_score, compute_stability_index, compute_disease_risk_momentum,
    estimate_biological_age, compute_health_balance_dimensions,
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

    # Health Recovery Score (today & yesterday)
    from datetime import timedelta
    today_data = HealthData.objects.filter(user=request.user, date=today).first()
    yesterday = today - timedelta(days=1)
    yesterday_data = HealthData.objects.filter(user=request.user, date=yesterday).first()
    recovery_today = calculate_recovery_score(today_data, profile)
    recovery_yesterday = calculate_recovery_score(yesterday_data, profile)

    # Health Stability Index (predictive behavior score)
    stability_index = compute_stability_index(health_data_list)

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
        'stability_index': stability_index,
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
        notes = request.POST.get('notes', '')

        systolic_bp = request.POST.get('systolic_bp')
        diastolic_bp = request.POST.get('diastolic_bp')
        fasting_sugar = request.POST.get('fasting_sugar')
        post_meal_sugar = request.POST.get('post_meal_sugar')
        
        # Get the last entry date for this user
        last_entry = HealthData.objects.filter(user=request.user).order_by('-date').first()
        
        # If there's a last entry, use next day; otherwise use today
        if last_entry:
            entry_date = last_entry.date + timedelta(days=1)
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
            notes=notes,
            systolic_bp=int(systolic_bp) if systolic_bp else None,
            diastolic_bp=int(diastolic_bp) if diastolic_bp else None,
            fasting_sugar=float(fasting_sugar) if fasting_sugar else None,
            post_meal_sugar=float(post_meal_sugar) if post_meal_sugar else None,
        )
        
        # Update nutrition totals from food entries for this date
        update_nutrition_totals(request.user, entry_date)
        
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
            }
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

    from datetime import date, timedelta
    today = date.today()
    yesterday = today - timedelta(days=1)
    today_data = HealthData.objects.filter(user=request.user, date=today).first()
    yesterday_data = HealthData.objects.filter(user=request.user, date=yesterday).first()
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


def _cardiometabolic_bp_category(systolic, diastolic):
    """Classify BP by standard ranges (systolic/diastolic). Returns (label, bootstrap badge class)."""
    if systolic is None and diastolic is None:
        return None, None
    s = systolic or 0
    d = diastolic  # None when not entered
    if s >= 140 or (d is not None and d >= 90):
        return 'Stage 2', 'danger'
    if 130 <= s <= 139 or (d is not None and 80 <= d <= 89):
        return 'Stage 1', 'warning'
    if 120 <= s <= 129 and (d is None or d < 80):
        return 'Elevated', 'warning'
    if s < 120 and (d is None or d < 80):
        return 'Normal', 'success'
    return 'Normal', 'success'


def _cardiometabolic_sugar_category(fasting_sugar):
    """Classify fasting glucose. Returns (label, bootstrap badge class)."""
    if fasting_sugar is None:
        return None, None
    if fasting_sugar < 100:
        return 'Normal', 'success'
    if 100 <= fasting_sugar <= 125:
        return 'Prediabetic', 'warning'
    return 'Diabetic risk', 'danger'


def _trend_direction(values):
    """Values ordered by date (oldest first). Returns 'increasing', 'stable', or 'decreasing'."""
    if not values or len(values) < 2:
        return 'stable'
    n = len(values)
    first_half = values[: max(1, n // 2)]
    second_half = values[-max(1, n // 2):]
    avg_first = sum(first_half) / len(first_half)
    avg_second = sum(second_half) / len(second_half)
    diff = avg_second - avg_first
    if diff > 0.5:
        return 'increasing'
    if diff < -0.5:
        return 'decreasing'
    return 'stable'


@login_required
def analytics_cardiometabolic(request):
    """Cardiometabolic risk monitoring: analyze user-entered BP and glucose, show risk trends only."""
    entries = list(
        HealthData.objects.filter(user=request.user)
        .filter(
            Q(systolic_bp__isnull=False) | Q(diastolic_bp__isnull=False)
            | Q(fasting_sugar__isnull=False) | Q(post_meal_sugar__isnull=False)
        )
        .order_by('date')
    )
    # Entries that have at least one cardiometabolic value
    entries_bp = [e for e in entries if e.systolic_bp is not None or e.diastolic_bp is not None]
    entries_sugar = [e for e in entries if e.fasting_sugar is not None]

    latest = entries[-1] if entries else None
    bp_category_label, bp_badge = None, None
    sugar_category_label, sugar_badge = None, None
    if latest:
        if latest.systolic_bp is not None or latest.diastolic_bp is not None:
            bp_category_label, bp_badge = _cardiometabolic_bp_category(latest.systolic_bp, latest.diastolic_bp)
        if latest.fasting_sugar is not None:
            sugar_category_label, sugar_badge = _cardiometabolic_sugar_category(latest.fasting_sugar)

    # Weekly trend direction (last 7 entries with values)
    bp_systolic_series = [e.systolic_bp for e in entries_bp if e.systolic_bp is not None]
    sugar_series = [e.fasting_sugar for e in entries_sugar]
    bp_trend = _trend_direction(bp_systolic_series) if len(bp_systolic_series) >= 2 else 'stable'
    sugar_trend = _trend_direction(sugar_series) if len(sugar_series) >= 2 else 'stable'

    # Chart data (last 30 points) as JSON for template
    chart_entries = entries[-30:] if len(entries) > 30 else entries
    chart_labels = [e.date.strftime('%Y-%m-%d') for e in chart_entries]
    chart_systolic = [e.systolic_bp for e in chart_entries]
    chart_diastolic = [e.diastolic_bp for e in chart_entries]
    chart_fasting = [e.fasting_sugar for e in chart_entries]
    chart_labels_json = json.dumps(chart_labels)
    chart_systolic_json = json.dumps(chart_systolic)
    chart_diastolic_json = json.dumps(chart_diastolic)
    chart_fasting_json = json.dumps(chart_fasting)
    show_chart = len(chart_entries) >= 2 and (any(x is not None for x in chart_systolic) or any(x is not None for x in chart_fasting))

    return render(request, 'analytics_cardiometabolic.html', {
        'latest': latest,
        'bp_category_label': bp_category_label,
        'bp_badge': bp_badge,
        'sugar_category_label': sugar_category_label,
        'sugar_badge': sugar_badge,
        'bp_trend': bp_trend,
        'sugar_trend': sugar_trend,
        'entries_bp': entries_bp,
        'entries_sugar': entries_sugar,
        'chart_labels_json': chart_labels_json,
        'chart_systolic_json': chart_systolic_json,
        'chart_diastolic_json': chart_diastolic_json,
        'chart_fasting_json': chart_fasting_json,
        'show_chart': show_chart,
        'has_any_data': len(entries) > 0,
    })


@login_required
def analytics_risk_momentum(request):
    """Health Risk Momentum Tracker based on disease risk trends."""

    predictions = list(
        DiseasePrediction.objects.filter(user=request.user)
        .order_by('created_at')
    )

    momentum = compute_disease_risk_momentum(predictions) or []

    # Safe absolute value calculation
    for item in momentum:
        change = item.get("change_per_week", 0)
        item["abs_change_per_week"] = abs(change)

    primary_series_labels = '[]'
    primary_series_values = '[]'
    primary_disease = None
    primary_momentum = None

    if momentum:
        primary_momentum = momentum[0]
        primary_disease = primary_momentum['disease']

        series = [
            p for p in predictions
            if p.disease_type == primary_disease
        ]

        series_sorted = sorted(series, key=lambda x: x.created_at)

        labels = [p.created_at.strftime('%Y-%m-%d') for p in series_sorted]
        values = [round(p.risk_score, 1) for p in series_sorted]

        import json
        primary_series_labels = json.dumps(labels)
        primary_series_values = json.dumps(values)

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

    radar_labels = ['Sleep', 'Exercise', 'Nutrition', 'Recovery', 'Stability', 'Metabolic']
    radar_values = [
        balance['sleep'],
        balance['exercise'],
        balance['nutrition'],
        balance['recovery'],
        balance['stability'],
        balance['metabolic'],
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
        
    health_data_list = list(HealthData.objects.filter(user=request.user).order_by('date'))
    has_sufficient_data = len(health_data_list) >= 1
    
    if request.method == 'POST':
        if not has_sufficient_data:
            messages.error(request, 'Not enough data for analysis.')
            return redirect('analytics_correlation')

        analysis_data = generate_correlation_analysis(health_data_list)
        
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
    
    health_data_list = list(HealthData.objects.filter(user=request.user).order_by('date'))
    
    if len(health_data_list) < 1:
        return JsonResponse({'error': 'Add at least 1 data point for analysis'}, status=400)
    
    analysis_data = generate_correlation_analysis(health_data_list)
    
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
        reminder = Reminder.objects.create(
            user=request.user,
            reminder_type=request.POST.get('reminder_type'),
            time=request.POST.get('time'),
            message=request.POST.get('message', ''),
            days_of_week=request.POST.getlist('days_of_week') or list(range(7)),
        )
        return JsonResponse({
            'success': True,
            'reminder': {
                'id': reminder.id,
                'type': reminder.reminder_type,
                'time': reminder.time.strftime('%H:%M'),
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

