"""
Include this in your project's urls.py:

    from django.urls import path, include
    urlpatterns = [
        ...
        path('api/', include('esim_checker.urls')),
    ]

Resulting endpoint: /api/device_compatibility_checker/
"""
from django.urls import path
from .views import DeviceCompatibilityCheckerView

app_name = 'esim_checker'

urlpatterns = [
    # Note: original request used 'decive_compatibility_checker' (typo).
    # Both spellings are accepted here for backward compatibility.
    path(
        'device_compatibility_checker/',
        DeviceCompatibilityCheckerView.as_view(),
        name='device_compatibility_checker',
    ),
    path(
        'decive_compatibility_checker/',   # legacy typo alias
        DeviceCompatibilityCheckerView.as_view(),
        name='device_compatibility_checker_alias',
    ),
]
