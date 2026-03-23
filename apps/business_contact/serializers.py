from rest_framework import serializers
from .models import BusinessContact


class BusinessContactSerializer(serializers.ModelSerializer):
    class Meta:
        model  = BusinessContact
        fields = ["id", "full_name", "business_name", "business_email", "business_needs", "message", "created_at"]
