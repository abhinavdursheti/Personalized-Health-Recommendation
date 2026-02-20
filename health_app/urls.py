"""
URL configuration for health_app project.
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('recommendation.urls')),
    path('api/', include('recommendation.urls')),
]


