from django.urls import path
from .views import HealthCheckView, AnalyzeView

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health-check'),
    path('analyze/', AnalyzeView.as_view(), name='analyze-website'),
]