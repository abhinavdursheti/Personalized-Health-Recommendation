import os
import django
from datetime import date, timedelta
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'health_app.settings')
django.setup()

from recommendation.models import HealthData
from django.contrib.auth.models import User

user = User.objects.first()
latest_entries = HealthData.objects.filter(user=user).order_by('-date')[:5]

print("=== LATEST ENTRIES ===")
for e in latest_entries:
    print(f"ID: {e.id}, Date: {e.date}, Weight: {e.weight}")

latest = latest_entries.first()
if latest:
    new_date = latest.date + timedelta(days=1)
    print(f"\nNext generated date would be: {new_date}")
else:
    print("No entries.")
