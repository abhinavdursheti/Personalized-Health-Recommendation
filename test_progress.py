import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'health_app.settings')
django.setup()

from recommendation.models import HealthData
from django.contrib.auth.models import User
from recommendation.utils import assess_progress

user = User.objects.get(username='testuser2')  # or just first()
data = list(HealthData.objects.filter(user=user).order_by('date'))

if len(data) >= 2:
    print(f"Weight entries (chronological): {[d.weight for d in data[-3:]]}")
    res = assess_progress(user.userprofile, data)
    print(f"assess_progress output:\n {res}")
else:
    print("Not enough data to test.")
