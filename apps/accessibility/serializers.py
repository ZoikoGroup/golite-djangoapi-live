from rest_framework import serializers
from .models import AccessibilityIssue

class AccessibilityIssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessibilityIssue
        fields = '__all__'