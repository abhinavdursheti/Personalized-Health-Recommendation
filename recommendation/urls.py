from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Authentication
    path("analytics/habit-streak/", views.analytics_habit_streak, name="analytics_habit_streak"),
    path('', views.index, name='index'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Dashboards (split)
    path('dashboard/', views.dashboard_overview, name='dashboard'),
    path('dashboard/overview/', views.dashboard_overview, name='dashboard_overview'),
    path('dashboard/activity/', views.dashboard_activity, name='dashboard_activity'),
    path('dashboard/nutrition/', views.dashboard_nutrition, name='dashboard_nutrition'),
    path('dashboard/alerts/', views.dashboard_alerts, name='dashboard_alerts'),
    path('dashboard/insights/', views.dashboard_insights, name='dashboard_insights'),
    path('setup-profile/', views.setup_profile, name='setup_profile'),
    # Recommendations
    path('recommendations/', views.recommendations, name='recommendations'),
    path('recommendations/diet/', views.diet_recommendation, name='diet_recommendation'),
    path('recommendations/exercise/', views.exercise_recommendation, name='exercise_recommendation'),
    path('recommendations/sleep/', views.sleep_recommendation, name='sleep_recommendation'),
    
    # Analytics
    path('analytics/', views.analytics, name='analytics'),
    path('analytics/recovery/', views.analytics_recovery, name='analytics_recovery'),
    path('analytics/correlation/', views.analytics_correlation, name='analytics_correlation'),
    path('analytics/habits/', views.analytics_habits, name='analytics_habits'),
    path('analytics/biological-age/', views.analytics_biological_age, name='analytics_biological_age'),
    path('analytics/health-balance/', views.analytics_health_balance, name='analytics_health_balance'),
    path('analytics/risk-momentum/', views.analytics_risk_momentum, name='analytics_risk_momentum'),
    path('analytics/habit-streak/', views.analytics_habit_streak, name='analytics_habit_streak'),

    # Simulator
    path('simulator/', views.simulator, name='simulator'),
    path('api/run-simulation/', views.run_simulation, name='run_simulation'),
    
    # API endpoints
    path('api/generate-recommendation/', views.generate_recommendation, name='generate_recommendation'),
    path('api/add-health-data/', views.add_health_data, name='add_health_data'),
    path('api/delete-health-data/<int:data_id>/', views.delete_health_data, name='delete_health_data'),
    path('api/generate-recovery-analysis/', views.generate_recovery_analysis, name='generate_recovery_analysis'),
    path('api/generate-correlation-analysis/', views.generate_correlation_analysis_view, name='generate_correlation_analysis'),
    path('api/generate-habit-analysis/', views.generate_habit_analysis, name='generate_habit_analysis'),
    path('api/generate-disease-prediction/', views.generate_disease_prediction, name='generate_disease_prediction'),
    path('api/create-reminder/', views.create_reminder, name='create_reminder'),
    path('api/toggle-reminder/<int:reminder_id>/', views.toggle_reminder, name='toggle_reminder'),
    path('api/delete-reminder/<int:reminder_id>/', views.delete_reminder, name='delete_reminder'),
    path('api/mark-alert-read/<int:alert_id>/', views.mark_alert_read, name='mark_alert_read'),
    path('api/add-food-entry/', views.add_food_entry, name='add_food_entry'),
    path('api/delete-food-entry/<int:entry_id>/', views.delete_food_entry, name='delete_food_entry'),
    path('api/get-food-suggestions/', views.get_food_suggestions_view, name='get_food_suggestions'),
    path('api/get-food-replacements/', views.get_food_replacements_view, name='get_food_replacements'),
]

