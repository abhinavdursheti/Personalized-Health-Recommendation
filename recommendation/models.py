from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import date


class UserProfile(models.Model):
    """Extended user profile with health information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(120)])
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')])
    height = models.FloatField(help_text="Height in cm", validators=[MinValueValidator(50), MaxValueValidator(250)])
    weight = models.FloatField(help_text="Weight in kg", validators=[MinValueValidator(20), MaxValueValidator(300)])
    activity_level = models.CharField(
        max_length=20,
        choices=[
            ('sedentary', 'Sedentary (little or no exercise)'),
            ('light', 'Lightly active (light exercise 1-3 days/week)'),
            ('moderate', 'Moderately active (moderate exercise 3-5 days/week)'),
            ('active', 'Very active (hard exercise 6-7 days/week)'),
            ('very_active', 'Extra active (very hard exercise, physical job)'),
        ],
        default='sedentary'
    )
    health_goal = models.CharField(
        max_length=20,
        choices=[
            ('weight_loss', 'Weight Loss'),
            ('muscle_gain', 'Muscle Gain'),
            ('maintenance', 'Weight Maintenance'),
            ('general', 'General Wellness'),
        ],
        default='general'
    )
    dietary_preference = models.CharField(
        max_length=20,
        choices=[
            ('none', 'No Preference'),
            ('vegetarian', 'Vegetarian'),
            ('vegan', 'Vegan'),
            ('keto', 'Keto'),
            ('paleo', 'Paleo'),
        ],
        default='none'
    )
    allergies = models.TextField(blank=True, help_text="Comma-separated list of allergies")
    medical_conditions = models.TextField(blank=True, help_text="Any medical conditions")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def bmi(self):
        """Calculate BMI"""
        height_m = self.height / 100
        return round(self.weight / (height_m ** 2), 2)

    @property
    def bmr(self):
        """Calculate Basal Metabolic Rate using Mifflin-St Jeor Equation"""
        if self.gender == 'M':
            bmr = 10 * self.weight + 6.25 * self.height - 5 * self.age + 5
        else:
            bmr = 10 * self.weight + 6.25 * self.height - 5 * self.age - 161
        return round(bmr, 2)

    @property
    def tdee(self):
        """Calculate Total Daily Energy Expenditure"""
        activity_multipliers = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'active': 1.725,
            'very_active': 1.9,
        }
        return round(self.bmr * activity_multipliers.get(self.activity_level, 1.2), 2)

    def __str__(self):
        return f"{self.user.username}'s Profile"


class HealthData(models.Model):
    """Track user's health data over time"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=date.today)
    weight = models.FloatField(validators=[MinValueValidator(20), MaxValueValidator(300)])
    sleep_hours = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(24)], null=True, blank=True)
    exercise_minutes = models.IntegerField(validators=[MinValueValidator(0)], null=True, blank=True)
    calories_consumed = models.FloatField(validators=[MinValueValidator(0)], null=True, blank=True)
    water_intake_liters = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(10)], null=True, blank=True, help_text="Water intake in liters")
    notes = models.TextField(blank=True)
    
    # Calculated nutrition totals (from food entries)
    total_calories = models.FloatField(default=0, help_text="Total calories from food entries")
    total_protein = models.FloatField(default=0, help_text="Total protein in grams")
    total_carbs = models.FloatField(default=0, help_text="Total carbs in grams")
    total_fats = models.FloatField(default=0, help_text="Total fats in grams")
    total_fiber = models.FloatField(default=0, help_text="Total fiber in grams")

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.username} - {self.date}"


class Recommendation(models.Model):
    """Store generated recommendations"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recommendation_type = models.CharField(
        max_length=20,
        choices=[
            ('diet', 'Diet'),
            ('exercise', 'Exercise'),
            ('sleep', 'Sleep'),
        ]
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    details = models.JSONField(default=dict)  # Store structured recommendation data
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.recommendation_type} - {self.title}"


class RecoveryStabilityAnalysis(models.Model):
    """Store recovery and stability predictions"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recovery_days = models.FloatField(help_text="Predicted days to recover from setback")
    stability_score = models.FloatField(help_text="Stability score (0-100)")
    is_stable = models.BooleanField(default=False)
    risk_level = models.CharField(max_length=10, choices=[('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High')])
    consistency_score = models.FloatField(default=0.0)
    adherence_rate = models.FloatField(default=0.0)
    streak_days = models.IntegerField(default=0)
    recommendations = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        get_latest_by = 'created_at'

    def __str__(self):
        return f"{self.user.username} - Recovery: {self.recovery_days} days, Stability: {self.stability_score}%"


class BehaviorCorrelationAnalysis(models.Model):
    """Store behavior-cause correlation insights"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    insights = models.JSONField(default=list)  # List of behavior insights
    correlations = models.JSONField(default=dict)  # Correlation coefficients
    root_causes = models.JSONField(default=list)  # Identified root causes
    data_points_analyzed = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        get_latest_by = 'created_at'

    def __str__(self):
        return f"{self.user.username} - {len(self.insights)} insights, {len(self.root_causes)} root causes"


class HabitSensitivityAnalysis(models.Model):
    """Store habit sensitivity and fragility analysis"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    habits = models.JSONField(default=list)  # List of analyzed habits
    fragile_habits = models.JSONField(default=list)
    resilient_habits = models.JSONField(default=list)
    high_impact_habits = models.JSONField(default=list)
    total_habits_analyzed = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        get_latest_by = 'created_at'

    def __str__(self):
        return f"{self.user.username} - {self.total_habits_analyzed} habits analyzed"


class Reminder(models.Model):
    """Reminders for food, water, and other health activities"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reminder_type = models.CharField(
        max_length=20,
        choices=[
            ('food', 'Food/Meal'),
            ('water', 'Water'),
            ('exercise', 'Exercise'),
            ('medication', 'Medication'),
            ('sleep', 'Sleep'),
        ]
    )
    time = models.TimeField(help_text="Time for reminder")
    message = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    days_of_week = models.JSONField(default=list, help_text="Days of week (0=Monday, 6=Sunday)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['time']

    def __str__(self):
        return f"{self.user.username} - {self.reminder_type} at {self.time}"


class HealthRiskAlert(models.Model):
    """Store health risk alerts and warnings"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    risk_level = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Low Risk'),
            ('medium', 'Medium Risk'),
            ('high', 'High Risk'),
            ('critical', 'Critical Risk'),
        ]
    )
    alert_type = models.CharField(
        max_length=50,
        choices=[
            ('weight', 'Weight Issue'),
            ('bmi', 'BMI Risk'),
            ('sleep', 'Sleep Deprivation'),
            ('exercise', 'Lack of Exercise'),
            ('diet', 'Poor Diet'),
            ('disease', 'Disease Risk'),
        ]
    )
    message = models.TextField()
    recommendations = models.JSONField(default=list)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.risk_level} - {self.alert_type}"


class DiseasePrediction(models.Model):
    """Store disease risk predictions"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    disease_type = models.CharField(max_length=100)
    risk_score = models.FloatField(help_text="Risk score (0-100)")
    risk_level = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Low Risk'),
            ('medium', 'Medium Risk'),
            ('high', 'High Risk'),
        ]
    )
    factors = models.JSONField(default=list, help_text="Contributing factors")
    recommendations = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        get_latest_by = 'created_at'

    def __str__(self):
        return f"{self.user.username} - {self.disease_type} ({self.risk_level})"


class FoodEntry(models.Model):
    """Track individual food items consumed"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    health_data = models.ForeignKey(HealthData, on_delete=models.CASCADE, related_name='food_entries', null=True, blank=True)
    date = models.DateField(default=date.today)
    meal_type = models.CharField(
        max_length=20,
        choices=[
            ('breakfast', 'Breakfast'),
            ('lunch', 'Lunch'),
            ('dinner', 'Dinner'),
            ('snacks', 'Snacks'),
        ]
    )
    food_name = models.CharField(max_length=200)
    quantity = models.FloatField(help_text="Quantity (servings or grams)", default=1.0)
    unit = models.CharField(max_length=20, default='serving', help_text="Unit: serving, gram, cup, etc.")
    
    # Nutritional values per unit
    calories_per_unit = models.FloatField(default=0)
    protein_per_unit = models.FloatField(default=0)
    carbs_per_unit = models.FloatField(default=0)
    fats_per_unit = models.FloatField(default=0)
    fiber_per_unit = models.FloatField(default=0)
    
    # Calculated totals
    total_calories = models.FloatField(default=0)
    total_protein = models.FloatField(default=0)
    total_carbs = models.FloatField(default=0)
    total_fats = models.FloatField(default=0)
    total_fiber = models.FloatField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date', 'meal_type']
    
    def save(self, *args, **kwargs):
        # Calculate totals based on quantity
        self.total_calories = round(self.calories_per_unit * self.quantity, 2)
        self.total_protein = round(self.protein_per_unit * self.quantity, 2)
        self.total_carbs = round(self.carbs_per_unit * self.quantity, 2)
        self.total_fats = round(self.fats_per_unit * self.quantity, 2)
        self.total_fiber = round(self.fiber_per_unit * self.quantity, 2)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.username} - {self.meal_type} - {self.food_name} ({self.quantity} {self.unit})"

