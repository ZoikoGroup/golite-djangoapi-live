from django.contrib import admin
from .models import AccessibilityIssue


@admin.register(AccessibilityIssue)
class AccessibilityIssueAdmin(admin.ModelAdmin):
    list_display = (
        'full_name',
        'email',
        'issue_type',
        'email_sent',   # ✅ NEW
        'created_at'
    )

    search_fields = ('full_name', 'email', 'issue_type')

    list_filter = (
        'issue_type',
        'email_sent',   # ✅ NEW (filter by sent/failed)
        'created_at'
    )

    list_editable = ('email_sent',)  # ✅ optional (manual toggle)

    ordering = ('-created_at',)