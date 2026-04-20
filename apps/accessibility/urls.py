from django.urls import path
from .views import AccessibilityIssueCreateView

urlpatterns = [
    path('accessibility-report/', AccessibilityIssueCreateView.as_view(), name='accessibility-report'),
]