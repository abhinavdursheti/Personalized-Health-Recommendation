import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'health_app.settings')
django.setup()

from recommendation.models import HealthData
from django.contrib.auth.models import User
from recommendation.utils import (
    calculate_recovery_score, generate_correlation_analysis,
    estimate_biological_age, compute_health_balance_dimensions,
    calculate_health_risk
)

user = User.objects.get(username='testuser2') 
profile = user.userprofile
data = list(HealthData.objects.filter(user=user).order_by('date'))

print("=== 1. Recovery Score ===")
rec = calculate_recovery_score(data[-1], profile)
print(f"Latest Recovery Score: {rec}")

print("\n=== 2. Correlation Engine ===")
corr = generate_correlation_analysis(data, 2000)
print(f"Top Correlation keys: {corr['correlations'].keys() if corr['correlations'] else 'None'}")
print(f"First insight: {corr['insights'][0]['insight'] if corr['insights'] else 'None'}")

print("\n=== 3. Biological Age Estimator ===")
bio = estimate_biological_age(profile, data)
print(f"Chronological: {bio['chronological_age']}, Biological: {bio['biological_age']}, Delta: {bio['delta_years']}")

print("\n=== 4. Health Balance Radar ===")
bal = compute_health_balance_dimensions(profile, data)
print(f"Balance dimensions: {bal}")

print("\n=== 5. Risk Momentum (Risk Calculation) ===")
risk = calculate_health_risk(profile, data[-7:])
print(f"Recent Risk Score: {risk['risk_score']}")

print("\n=== All Analytics Computations Passed! ===")
