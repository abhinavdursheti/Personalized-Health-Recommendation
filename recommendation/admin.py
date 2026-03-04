from django.contrib import admin
from .models import UserProfile, HealthData, Recommendation, RecoveryStabilityAnalysis, BehaviorCorrelationAnalysis, HabitSensitivityAnalysis, Reminder, HealthRiskAlert, DiseasePrediction, FoodEntry


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'age', 'gender', 'bmi', 'health_goal', 'activity_level']
    list_filter = ['health_goal', 'activity_level', 'gender']
    search_fields = ['user__username', 'user__email']


@admin.register(HealthData)
class HealthDataAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'weight', 'sleep_hours', 'exercise_minutes', 'calories_consumed']
    list_filter = ['date']
    search_fields = ['user__username']
    date_hierarchy = 'date'


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ['user', 'recommendation_type', 'title', 'created_at', 'is_active']
    list_filter = ['recommendation_type', 'is_active', 'created_at']
    search_fields = ['user__username', 'title']
    date_hierarchy = 'created_at'


@admin.register(RecoveryStabilityAnalysis)
class RecoveryStabilityAnalysisAdmin(admin.ModelAdmin):
    list_display = ['user', 'recovery_days', 'stability_score', 'risk_level', 'created_at']
    list_filter = ['risk_level', 'is_stable', 'created_at']
    search_fields = ['user__username']
    date_hierarchy = 'created_at'


@admin.register(BehaviorCorrelationAnalysis)
class BehaviorCorrelationAnalysisAdmin(admin.ModelAdmin):
    list_display = ['user', 'data_points_analyzed', 'created_at']
    search_fields = ['user__username']
    date_hierarchy = 'created_at'


@admin.register(HabitSensitivityAnalysis)
class HabitSensitivityAnalysisAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_habits_analyzed', 'created_at']
    search_fields = ['user__username']
    date_hierarchy = 'created_at'


@admin.register(Reminder)
class ReminderAdmin(admin.ModelAdmin):
    list_display = ['user', 'reminder_type', 'time', 'is_active', 'created_at']
    list_filter = ['reminder_type', 'is_active', 'created_at']
    search_fields = ['user__username', 'message']


@admin.register(HealthRiskAlert)
class HealthRiskAlertAdmin(admin.ModelAdmin):
    list_display = ['user', 'risk_level', 'alert_type', 'is_read', 'created_at']
    list_filter = ['risk_level', 'alert_type', 'is_read', 'created_at']
    search_fields = ['user__username', 'message']
    date_hierarchy = 'created_at'


@admin.register(DiseasePrediction)
class DiseasePredictionAdmin(admin.ModelAdmin):
    list_display = ['user', 'disease_type', 'risk_score', 'risk_level', 'created_at']
    list_filter = ['risk_level', 'disease_type', 'created_at']
    search_fields = ['user__username', 'disease_type']
    date_hierarchy = 'created_at'


@admin.register(FoodEntry)
class FoodEntryAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'meal_type', 'food_name', 'quantity', 'total_calories', 'created_at']
    list_filter = ['meal_type', 'date', 'created_at']
    search_fields = ['user__username', 'food_name']
    date_hierarchy = 'date'

