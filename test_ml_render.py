import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'health_app.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from recommendation.views import _build_dashboard_context

for user in User.objects.all():
    print(f"Testing user: {user.username}")
    req = RequestFactory().get('/dashboard/')
    req.user = user
    try:
        ctx = _build_dashboard_context(req)
        print(f"  ML Preds: {bool(ctx.get('ml_predictions'))}")
        if ctx.get('ml_predictions'):
            print(f"  {ctx.get('ml_predictions')}")
    except Exception as e:
        print(f"  Error: {e}")
