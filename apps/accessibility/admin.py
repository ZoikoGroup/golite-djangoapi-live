from django.contrib import admin
from .models import AccessibilityIssue

@admin.register(AccessibilityIssue)
class AccessibilityIssueAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'issue_type', 'created_at')
    search_fields = ('full_name', 'email', 'issue_type')
    list_filter = ('issue_type', 'created_at')