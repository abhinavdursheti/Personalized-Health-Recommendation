import os
import django
from datetime import date, timedelta
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'health_app.settings')
django.setup()

from recommendation.models import HealthData
from django.contrib.auth.models import User

user = User.objects.first()

latest_entry = HealthData.objects.filter(user=user).order_by('-date').first()
if latest_entry:
    entry_date = latest_entry.date + timedelta(days=1)
else:
    entry_date = date.today()

print(f"Creating entry for user {user.username} with date: {entry_date}")
hd = HealthData.objects.create(
    user=user,
    date=entry_date,
    weight=70.0,
    stress_level=5,
    daily_steps=1000
)

print(f"Created HealthData ID {hd.id}. Checking DB for saved date...")

hd.refresh_from_db()
print(f"Refreshed from DB, date is: {hd.date}")

